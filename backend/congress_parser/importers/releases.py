"""
US Code XML release point importer.

Downloads and parses US Code XML releases from uscode.house.gov. The US Code
is published as a set of XML files (one per title, e.g. usc01.xml through usc54.xml)
packaged in ZIP archives at periodic "release points" tied to Public Law numbers.

US Code XML structure (USLM schema, simplified):
    <uscDoc>
        <title identifier="/us/usc/t42">
            <chapter identifier="/us/usc/t42/ch7">
                <subchapter identifier="/us/usc/t42/ch7/schXVIII">
                    <section id="GUID" identifier="/us/usc/t42/s1395">
                        <num value="1395">§1395.</num>
                        <heading>Prohibition against...</heading>
                        <content>Full text...</content>
                        <subsection id="GUID" identifier="/us/usc/t42/s1395/a">
                            ...
                        </subsection>
                    </section>
                </subchapter>
            </chapter>
        </title>
    </uscDoc>

Key attributes on elements:
    - identifier: Hierarchical path (e.g. "/us/usc/t42/s1395/a/1")
    - id: Unique GUID for the element
    - value: Display number on <num> elements (e.g. "1395")

Pipeline:
    1. Scrape uscode.house.gov/download/priorreleasepoints.htm for release URLs
    2. Download ZIP archive for each release point
    3. For each title XML in the ZIP, parse the hierarchy into USCSection/USCContent
    4. Store in database with version tracking for diff computation
"""

import argparse
import html
import string
import os
from unidecode import unidecode  # GPLV2
import zipfile
from datetime import datetime
from congress_parser.importers.bills import download_path
from joblib import Parallel, delayed
import requests
from sqlalchemy import func
from congress_db.session import import_title, get_number, Session
from congress_db.models import USCRelease, Version

THREADS = int(os.environ.get("PARSE_THREADS", -1))
DOWNLOAD_BASE = "https://uscode.house.gov/download/{}"
RELEASE_POINTS = "https://uscode.house.gov/download/priorreleasepoints.htm"

ribber = string.ascii_letters + string.digits

def main():
    parser = argparse.ArgumentParser(description="Process release points.")
    parser.add_argument(
        "--release-point",
        type=str,
        help="URL of the zip file to process a single release point",
    )
    args = parser.parse_args()

    if args.release_point:
        process_single_release_point(args.release_point)
    else:
        process_all_release_points()


def open_usc(file_str):
    """
    Parses a US Code title XML string and builds a lookup dictionary mapping
    each element's 'identifier' attribute to its lxml Element.

    Returns:
        tuple: (lookup_dict, elements_list) where lookup_dict maps identifiers
               like "/us/usc/t42/s1395" to Elements, and elements_list is the
               ordered list of all identified elements for sequential iteration.
    """
    lookup = {}
    usc_root = etree.fromstring(file_str)
    lookup["root"] = usc_root
    ids = usc_root.xpath("//*[@identifier]")
    for id in ids:
        lookup[id.attrib["identifier"]] = id
    return lookup, ids


def unidecode_str(input_str: str) -> str:
    return unidecode(input_str or "").replace("--", "-")

def get_number(ident: str) -> float:
    """
    Converts a usc_ident into a number that is supposed to impart some implicit order

    Args:
        ident (str): The usc ident

    Returns:
        float: The supposed order
    """
    ident = unidecode_str(ident)
    if "..." in ident:
        ident = ident.split("...")[0]
    result = re.search(
        r"^(\d*)([a-z]*)\s?(?:\-?t?o?(?:\.\.\.)?\.?)\s?(\d*)([a-z]*)$",
        ident,
        re.IGNORECASE,
    )
    grps = None
    try:
        grps = result.groups()
        tot = float(grps[0])
        subtot = 0
        if grps[1] != "":
            for i in grps[1]:
                subtot += ribber.index(i) / len(ribber)
        if grps[2] != "":
            subtot += float(grps[2]) / 100
        if grps[3] != "":
            subtot += (ribber.index(grps[3]) / len(ribber)) / 1000
        return tot
    except Exception as e:
        print(e)
        print("failed on ", ident, grps)
        return 0


def import_title(chapter_file, chapter_number, version_string, release: USCRelease):
    """
    Parses a single US Code title XML file and stores its hierarchical content.

    The USLM XML uses a nested structure where organizational elements (chapter,
    subchapter, part, etc.) contain sections, which in turn contain subsections,
    paragraphs, and subparagraphs. This function:

    1. Creates a USCChapter record for the title
    2. Iterates over all elements with 'identifier' attributes
    3. Creates USCSection records for organizational levels (chapter, subchapter, etc.)
    4. For leaf sections (identifier depth = 5, e.g. /us/usc/tXX/sYYY), recursively
       creates USCContent records for all nested content

    Args:
        chapter_file: Raw bytes of the XML file
        chapter_number: Title number string (e.g. "42")
        version_string: Version label (unused, kept for compatibility)
        release: Dict with usc_release_id and version_id for DB foreign keys
    """
    session = Session()
    release_id = release["usc_release_id"]

    version_id = release["version_id"]

    def recursive_content(section_id, content_id, search_element, order):
        """
        Recursively stores section content (subsections, paragraphs, etc.)
        as USCContent records. Each USLM element with both 'id' and 'identifier'
        attributes is a content node. Child layout mirrors bill XML:
            [0] = <num> (display number)
            [1] = <heading> (or <content>/<chapeau> if no heading)
            [2] = <content>/<chapeau>/<notes> (body text, if heading present)
        """
        if "id" in search_element.attrib and "identifier" in search_element.attrib:
            enum = search_element[0]
            heading = search_element[1]
            content_str = None
            if len(search_element) > 2:
                content_elem = search_element[2]
                if (
                    "content" in content_elem.tag
                    or "chapeau" in content_elem.tag
                    or "notes" in content_elem.tag
                ):
                    content_str = resolve_citations(
                        " ".join(content_elem.itertext()).strip().replace("\n", " "),
                        chapter_number,
                    )
            if "heading" in heading.tag:
                content = USCContent(
                    content_type=search_element.tag,
                    usc_guid=search_element.attrib["id"],
                    usc_ident=unidecode_str(search_element.attrib["identifier"]),
                    number=unidecode_str(enum.attrib["value"]),
                    section_display=enum.text,
                    usc_section_id=section_id,
                    parent_id=content_id,
                    content_str=unidecode_str(content_str),
                    order_number=order,
                    heading=unidecode_str(heading.text),
                    version_id=version_id,
                )
            else:
                content_elem = heading
                if (
                    "content" in content_elem.tag
                    or "chapeau" in content_elem.tag
                    or "notes" in content_elem.tag
                ):
                    content_str = resolve_citations(
                        " ".join(content_elem.itertext()).strip().replace("\n", " "),
                        chapter_number,
                    )
                content = USCContent(
                    content_type=search_element.tag,
                    usc_guid=search_element.attrib["id"],
                    usc_ident=unidecode_str(search_element.attrib["identifier"]),
                    number=enum.attrib["value"],
                    section_display=enum.text,
                    usc_section_id=section_id,
                    parent_id=content_id,
                    content_str=unidecode_str(content_str),
                    order_number=order,
                    heading=None,
                    version_id=version_id,
                )
            session.add(content)
            session.flush()
            order = 0
            for elem in search_element:
                if "id" in elem.attrib:
                    recursive_content(section_id, content.usc_content_id, elem, order)
                    order = order + 1

    chapter_root, elements = open_usc(chapter_file)
    for boi in chapter_root["root"].iter():
        if "heading" in boi.tag:
            title = boi.text
            break
    print(title)
    existing = (
        session.query(USCChapter)
        .filter(USCChapter.version_id == version_id)
        .filter(USCChapter.short_title == chapter_number)
        .first()
    )
    if existing:
        print(f"Chapter {chapter_number} alread imported for {version_id}")
        return None
    chap = USCChapter(
        short_title=chapter_number,
        long_title=title,
        document="usc",
        version_id=version_id,
        usc_release_id=release_id,
    )
    session.add(chap)
    session.flush()
    sections = []
    parents = {}
    # Track elements whose children should be handled by recursive_content
    # rather than top-level iteration. None is pre-seeded so root-level
    # elements pass through.
    is_handled = {None: True}
    current_parent = None
    current_depth = 0
    for elem in elements:
        # Elements use namespaced tags like "{http://xml.house.gov/...}section"
        # Strip the namespace to get the plain tag name
        split_tag = elem.tag.split("}")[-1]
        if split_tag in ["uscDoc", "title"]:
            # Top-level container elements — skip, we process their children
            continue
        identifier = elem.attrib.get("identifier")
        parent_identifier = elem.getparent().attrib.get("identifier")
        if parent_identifier in is_handled:
            is_handled[identifier] = True
            continue

        # Organizational levels per the USLM schema — these become USCSection
        # records that serve as containers in the hierarchy above individual sections
        if split_tag in [
            "chapter",
            "subchapter",
            "part",
            "subpart",
            "division",
            "subdivision",
            "article",
            "subarticle",
        ]:
            if parent_identifier in parents:
                current_depth = parents.get(parent_identifier).get("depth", 0) + 1
            else:
                current_depth = 0
            enum = elem[0]
            par_obj = USCSection(
                usc_guid=elem.attrib["id"],
                usc_ident=identifier,
                number=unidecode_str(enum.attrib["value"]),
                section_display=unidecode_str(enum.text),
                heading=unidecode_str(elem[1].text),
                version_id=version_id,
                usc_chapter_id=chap.usc_chapter_id,
                content_type=split_tag,
            )
            if parents.get(parent_identifier) is not None:
                par_obj.parent_id = parents.get(parent_identifier)[
                    "section"
                ].usc_section_id

            parents[identifier] = {
                "elem": elem,
                "depth": current_depth,
                "section": par_obj,
            }
            session.add(par_obj)
            session.flush()
            current_parent = identifier
            current_depth += 1
        else:
            # Check if this is a leaf section (depth 5 = /us/usc/tXX/sYYY).
            # These are the actual statute sections that contain subsections/text.
            # Identifier starts with "s" but not "st" (to exclude subtitles).
            chunks = identifier.split("/")
            if len(chunks) == 5:
                if chunks[-1][0] == "s" and chunks[-1][1] != "t":
                    is_handled[identifier] = True
                    enum = elem[0]
                    sect_obj = USCSection(
                        usc_guid=elem.attrib["id"],
                        usc_ident=identifier,
                        number=unidecode_str(enum.attrib["value"]),
                        section_display=unidecode_str(enum.text),
                        heading=unidecode_str(elem[1].text),
                        version_id=version_id,
                        usc_chapter_id=chap.usc_chapter_id,
                        parent_id=parents.get(current_parent)["section"].usc_section_id,
                        content_type=split_tag,
                    )
                    session.add(sect_obj)
                    session.flush()
                    recursive_content(sect_obj.usc_section_id, None, elem, 0)
    session.commit()

def process_single_release_point(url, release=None):
    zip_file_path = download_path(url)
    with zipfile.ZipFile(zip_file_path) as zip_file:
        if release is None:
            session = Session()
            new_version = Version(base_id=None)
            session.add(new_version)
            session.flush()
            release = USCRelease(
                short_title=zip_file_path.split("/")[-1].split(".")[0],
                effective_date=datetime.now(),
                long_title="",
                version_id=new_version.version_id,
            )
            session.add(release)
            session.commit()
        files = zip_file.namelist()
        files = sorted(
            files, key=lambda x: get_number(x.split(".")[0].replace("usc", ""))
        )
        Parallel(n_jobs=THREADS, verbose=5, backend="loky")(
            delayed(import_title)(
                zip_file.open(file).read(),
                file.split(".")[0].replace("usc", ""),
                None,  # Assuming title is not needed for single release point
                release.to_dict(),  # Assuming release_point.to_dict() is not needed for single release point
            )
            for file in files
        )


def process_all_release_points():
    """
    Scrapes the USLM prior release points page for download links and
    processes each release that isn't already in the database.

    Release points are published around December 21 of even-numbered years,
    corresponding to the end of each Congress. The ZIP filename contains the
    Public Law number (e.g. xml_uscAll@117-328.zip).
    """
    release_points = []
    response = requests.get(RELEASE_POINTS)
    tree = html.fromstring(response.content)

    for year in range(2022, datetime.now().year, 2):
        search_date = f"12/21/{year}"
        links = tree.xpath(f'//a[contains(text(), "{search_date}")]/@href')

        if len(links) > 0:
            link = links[0].replace("usc-rp", "xml_uscAll").replace(".htm", ".zip")
            zipPath = DOWNLOAD_BASE.format(link)
            match = re.search(r"@(\d+)-(\d+)\.zip", link)

            release_points.append(
                {
                    "date": search_date,
                    "short_title": f"Public Law {match.group(1)}-{match.group(2)}",
                    "long_title": "",
                    "url": zipPath,
                }
            )

    session = Session()
    for rp in release_points:
        existing_rp = (
            session.query(USCRelease)
            .filter(
                USCRelease.short_title == rp.get("short_title"),
                func.date(USCRelease.effective_date)
                == datetime.strptime(rp.get("date"), "%m/%d/%Y"),
            )
            .all()
        )
        if len(existing_rp) > 0:
            print("Already in DB - Skipping")
            continue
        new_version = Version(base_id=None)
        session.add(new_version)
        session.commit()
        release_point = USCRelease(
            short_title=rp.get("short_title"),
            effective_date=datetime.strptime(rp.get("date"), "%m/%d/%Y"),
            long_title=rp.get("long_title"),
            version_id=new_version.version_id,
        )
        session.add(release_point)
        session.commit()
        zip_file_path = download_path(rp.get("url"))
        with zipfile.ZipFile(f"usc/{zip_file_path}") as zip_file:
            files = zip_file.namelist()

            files = sorted(
                files, key=lambda x: get_number(x.split(".")[0].replace("usc", ""))
            )
            Parallel(n_jobs=THREADS, verbose=5, backend="multiprocessing")(
                delayed(import_title)(
                    zip_file.open(file).read(),
                    file.split(".")[0].replace("usc", ""),
                    rp.get("title"),
                    release_point.to_dict(),
                )
                for file in files  # if "09" in file
            )


if __name__ == "__main__":
    main()
