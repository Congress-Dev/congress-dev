import os
import re
import string
import time

from lxml import etree
from unidecode import unidecode  # GPLV2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from billparser.utils.citation import resolve_citations
from billparser.db.caching import query_callable, regions
from billparser.db.models import USCSection
from billparser.db.models import *

username = os.environ.get("db_user", "bills")
password = os.environ.get("db_pass", "bills")
table = os.environ.get("db_table", "uscode")
db_host = os.environ.get("db_host", "localhost:5401")
DATABASE_URI = f"postgresql://{username}:{password}@{db_host}/{table}"
print(DATABASE_URI)
engine = create_engine(DATABASE_URI, poolclass=NullPool, connect_args={'sslmode': "disable"})

Base.metadata.create_all(engine)

ribber = string.ascii_letters + string.digits

def create_session_function(engine, query_cls, retries=5, delay=5):
    """
    Returns a callable `Session` function with retry logic for creating sessions.

    Args:
        engine: The SQLAlchemy engine to bind the session to.
        query_cls: The custom query class to use with the session.
        retries: Number of retries before giving up. Default is 5.
        delay: Delay in seconds between retries. Default is 5.

    Returns:
        A callable `Session` function that creates a new session with retry logic.
    """
    def Session():
        for attempt in range(retries):
            try:
                # Create the session factory
                session_factory = sessionmaker(bind=engine, query_cls=query_cls)
                # Create a new session instance
                return session_factory()
            except Exception as e:
                if attempt < retries - 1:
                    print(f"Connection failed: {e}. Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print("Max retries reached. Could not establish a connection.")
                    raise

    return Session
Session = create_session_function(engine, query_cls=query_callable(regions))
def unidecode_str(input_str: str) -> str:
    return unidecode(input_str or "").replace("--", "-")


def open_usc(file_str):
    """
        Pulls out all elements that have an identifier attribute
    """
    lookup = {}
    usc_root = etree.fromstring(file_str)
    lookup["root"] = usc_root
    ids = usc_root.xpath("//*[@identifier]")
    for id in ids:
        lookup[id.attrib["identifier"]] = id
    return lookup, ids


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
        chapter_file: file pointer to an xml file
    """
    session = Session()
    release_id = release["usc_release_id"]

    version_id = release["version_id"]

    def recursive_content(section_id, content_id, search_element, order):
        # if it has an id it is probably a thingy
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
    is_handled = {None: True}
    current_parent = None
    current_depth = 0
    for elem in elements:
        # Iterate over all the elements
        split_tag = elem.tag.split("}")[-1]
        if split_tag in ["uscDoc", "title"]:
            # We do not want to handle these two
            continue
        identifier = elem.attrib.get("identifier")
        parent_identifier = elem.getparent().attrib.get("identifier")
        if parent_identifier in is_handled:
            is_handled[identifier] = True
            continue

        # According to the USLM guide, these are the levels we'll want to track
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
