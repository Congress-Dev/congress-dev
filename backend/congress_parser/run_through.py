"""
Bill XML parsing and ingestion pipeline.

This module is the primary entry point for parsing Congressional bill XML files
from govinfo.gov bulk data downloads. It handles:

1. Opening ZIP archives of bill XML files (one ZIP per congress/session/chamber)
2. Extracting bill metadata (title, dates, sponsors) via XPath queries
3. Recursively traversing the <legis-body> XML tree to store hierarchical
   bill content (sections, subsections, paragraphs) in the database
4. Parallelizing bill parsing across multiple processes via joblib

Bill XML structure (simplified):
    <bill>
        <dublinCore><dc:title>...</dc:title></dublinCore>
        <form><action><action-date date="...">...</action-date></action></form>
        <legis-body>
            <section id="..." >
                <enum>1.</enum>
                <header>Short title</header>
                <text>This Act may be cited as...</text>
                <subsection id="...">
                    <enum>(a)</enum>
                    <header>...</header>
                    <text>...</text>
                </subsection>
            </section>
        </legis-body>
    </bill>

ZIP filename convention: BILLS-{congress}{chamber}{number}{version}.xml
    e.g. BILLS-118hr1234ih.xml = 118th Congress, House, bill 1234, Introduced in House
"""

from collections import defaultdict
import os
import re
import sys
import time
import logging
import traceback
from zipfile import ZipFile
import hashlib
import datetime
import dateutil.parser as parser

# import pandas
from lxml import etree
from lxml.etree import Element
from unidecode import unidecode  # GPLV2

import sqlalchemy

from sqlalchemy import desc

from congress_parser.actions import ActionObject
from congress_parser.actions import determine_action as determine_action2
from congress_parser.actions.redesignate import redesignate

from congress_db.models import (
    Legislation,
    LegislationContent,
    LegislationVersion,
    LegislationVersionEnum,
    LegislationChamber,
    LegislationType,
    USCContentDiff,
    USCContent,
    Version,
    USCSection,
    USCRelease,
    Congress,
)
from congress_parser.metadata.sponsors import (
    extract_sponsors_from_form,
    extract_sponsors_from_api,
)

from congress_parser.utils.logger import LogContext
from congress_parser.utils.cite_parser import parse_action_for_cite, ActionObject
from congress_db.session import Session, init_session
from congress_parser.translater import translate_paragraph

from joblib import Parallel, delayed
from typing import Any, Dict, List, Optional
from functools import lru_cache

text_paths = ["legis-body/section/subsection/text", "legis-body/section/text"]

# Parses govinfo.gov bulk data filenames like "BILLS-118hr1234ih.xml" into components:
#   session=118, house=hr, bill_number=1234, bill_version=ih
filename_regex = re.compile(
    r"BILLS-(?P<session>\d\d\d)(?P<house>\D+)(?P<bill_number>\d+)(?P<bill_version>\D+)\.xml"
)
chamb = {"hr": "House", "s": "Senate"}
BASE_VERSION = 1
EXISTING_CONGRESS = {}
CURRENT_CONGRESS = None
# -1 tells joblib to use all available CPU cores
THREADS = int(os.environ.get("PARSE_THREADS", -1))


def strip_arr(arr: List[str]) -> List[str]:
    """
    Strips all the strings in the input array

    Args:
        arr (List[str]): List of strings to strip

    Returns:
        List[str]: Stripped strings
    """
    return [x.strip() for x in arr]


def convert_to_text(element: Element, inside_quote: bool = False) -> str:
    """
    Converts an element to a string, if there is a quote tag it will add quotes.

    Args:
        element (Element): Input element
        inside_quote (bool, optional): Doesn't actually do anything. Defaults to False.

    Returns:
        str: Stringified version of the element's text
    """
    ret = ""
    if element.tag == "quote":
        ret = '"'

    ret += element.text or ""
    for elem in element:
        ret += convert_to_text(elem, inside_quote or (element.tag == "quote"))
    if element.tag == "quote":
        ret += '"'
    return unidecode(ret + (element.tail or "")).replace("--", "-")


# Abbreviation map for bill content hierarchy levels, used in cite construction
ll = {"subsection": "ss", "paragraph": "p", "section": "s", "subparagraph": "sb"}


@lru_cache(maxsize=20)
def get_congress_from_session_number(session_number: int, session) -> int:
    congress = (
        session.query(Congress)
        .filter(Congress.session_number == session_number)
        .first()
    )
    if congress is None:
        return None
    return congress.congress_id


def find_or_create_bill(bill_obj: dict, title: str, session: "SQLAlchemy.session"):
    release_point = (
        session.query(USCRelease).order_by(desc(USCRelease.created_at)).limit(1).all()
    )
    new_version = Version(base_id=release_point[0].version_id)
    session.add(new_version)
    session.commit()
    existing_bill = (
        session.query(Legislation)
        .join(Congress, Legislation.congress_id == Congress.congress_id)
        .filter(Legislation.number == bill_obj["bill_number"])
        .filter(Legislation.chamber == LegislationChamber(bill_obj["chamber"]))
        .filter(Congress.session_number == int(bill_obj["congress_session"]))
        .all()
    )
    if len(existing_bill) > 0:
        new_bill = existing_bill[0]
    else:
        new_bill = Legislation(
            number=bill_obj["bill_number"],
            title=title,
            chamber=LegislationChamber(bill_obj["chamber"]),
            legislation_type=LegislationType.Bill,
            version_id=new_version.version_id,
            congress_id=get_congress_from_session_number(
                int(bill_obj["congress_session"]), session
            ),  # CURRENT_CONGRESS is set by the ensure_congress function
        )
        session.add(new_bill)
        session.commit()

    new_bill_version = LegislationVersion(
        legislation_id=new_bill.legislation_id,
        legislation_version=LegislationVersionEnum(bill_obj["bill_version"].upper()),
        version_id=new_version.version_id,
        created_at=datetime.datetime.now(),
    )
    session.add(new_bill_version)
    session.commit()
    return (new_bill, new_bill_version)


def recursive_bill_content(
    content_id: int,
    search_element: Element,
    order: int,
    legis_version_id: int,
    parents: dict,
    path: str,
    vers_id: int,
    parent_cite: str = "",
    session: "SQLAlchemy.session" = None,
) -> List[LegislationContent]:
    """
    Recursively traverses the bill XML tree starting from <legis-body>,
    creating LegislationContent records for each structural element.

    Bill XML elements follow a consistent child layout:
        [0] = <enum> (e.g. "(a)", "1.", "SEC. 2.")
        [1] = <header>/<heading> (section title) OR <text>/<content> if no heading
        [2] = <text>/<content>/<chapeau>/<notes> (body text, if heading exists)

    Only elements with an "id" attribute are considered structural (sections,
    subsections, paragraphs, etc.). Elements without "id" are skipped during
    recursion.
    """
    extracted_action = []
    res: List[LegislationContent] = []
    content = None

    if search_element.tag == "legis-body":
        # Root node of the bill body — container for all sections
        content = LegislationContent(
            content_type=search_element.tag,
            parent_id=content_id,
            order_number=order,
            legislation_version_id=legis_version_id,
            section_display=None,
            content_str=None,
        )
    elif ("id" in search_element.attrib) and len(search_element) > 1:
        # Structural element with children: extract enum, heading, and content text.
        # Child layout: [0]=enum, [1]=heading (or content if no heading), [2]=content text
        enum = search_element[0]
        heading = search_element[1]
        content_str = None
        if len(search_element) > 2:
            content_elem = search_element[2]
            if (
                "content" in content_elem.tag
                or "chapeau" in content_elem.tag
                or "notes" in content_elem.tag
                or "text" in content_elem.tag
            ):
                content_str = convert_to_text(content_elem)
        if "head" in heading.tag:
            # Standard case: [1] is a heading element (e.g. <header>, <heading>)
            content = LegislationContent(
                content_type=search_element.tag,
                parent_id=content_id,
                order_number=order,
                legislation_version_id=legis_version_id,
                section_display=enum.text,
                content_str=content_str,
                heading=heading.text if heading is not None else None,
                lc_ident=search_element.attrib.get("id", None),
            )
        else:
            # No heading — [1] is actually content/text, not a heading
            content_elem = heading
            if (
                "content" in content_elem.tag
                or "chapeau" in content_elem.tag
                or "notes" in content_elem.tag
                or "text" in content_elem.tag
            ):
                content_str = convert_to_text(content_elem)
            content = LegislationContent(
                content_type=search_element.tag,
                parent_id=content_id,
                order_number=order,
                legislation_version_id=legis_version_id,
                section_display=enum.text,
                content_str=content_str,
                # heading=heading.text if heading is not None else None,
            )
    else:
        logging.debug(
            f"Items look like: {search_element.tag} and {len(search_element)}"
        )
    if content is not None:
        # print(content.content_type, content.content_str)
        session.add(content)
    if True:
        root_path = search_element.getroottree().getpath(search_element)
        sections = root_path.split("/section")
        if len(sections) > 2 and search_element.tag != "legis-body":
            pass
        elif "quote" in root_path:
            # print("Within quote")
            pass
    if (search_element.tag == "legis-body" or "id" in search_element.attrib) and len(
        search_element
    ) > 0:
        if content is not None:
            content.action_parse = extracted_action
            session.commit()
        order = 0

        for elem in search_element:
            if "id" in elem.attrib:
                res.extend(
                    recursive_bill_content(
                        content.legislation_content_id,
                        elem,
                        order,
                        legis_version_id,
                        parents,
                        path,
                        vers_id,
                        parent_cite,
                        session=session,
                    )
                )
                order = order + 1
    return res


def check_for_existing_legislation_version(bill_obj: object) -> Optional[LegislationVersion]:
    session = Session()
    # Check to see if we've already ingested this bill
    existing_legis = (
        session.query(Legislation)
        .join(Congress, Legislation.congress_id == Congress.congress_id)
        .filter(
            Legislation.number == bill_obj["bill_number"],
            Legislation.chamber == LegislationChamber(bill_obj["chamber"]),
            Congress.session_number == int(bill_obj["congress_session"]),
        )
        .all()
    )
    if len(existing_legis) == 0:
        return False

    result = (
        session.query(LegislationVersion)
        .filter(
            LegislationVersion.legislation_version
            == LegislationVersionEnum(bill_obj["bill_version"].upper()),
            LegislationVersion.legislation_id == existing_legis[0].legislation_id,
        )
        .all()
    )
    return result[0] if len(result) > 0 else None


def retrieve_existing_legislations(session) -> List[dict]:
    """
    Retrieves the existing legislations from the database, we are interested in the fields
    that will tell us if our bill number and version already exists. This will let us avoid
    trying to parse those.
    """
    existing_legis = (
        session.query(
            Legislation.chamber,
            Legislation.number,
            LegislationVersion.legislation_version,
            Congress.session_number,
        )
        .join(
            LegislationVersion,
            Legislation.legislation_id == LegislationVersion.legislation_id,
        )
        .join(Congress, Legislation.congress_id == Congress.congress_id)
        .all()
    )
    return [
        {
            "chamber": x[0],
            "bill_number": x[1],
            "bill_version": x[2],
            "congress_session": x[3],
        }
        for x in existing_legis
    ]


def parse_bill(
    f: str, path: str, bill_obj: object, archive_obj: object
) -> LegislationVersion:
    """
    Parses a single bill's XML content and stores it in the database.

    Steps:
    1. Parse the raw XML string into an lxml Element tree
    2. Skip if this bill version was already ingested (idempotency check)
    3. Extract the bill title from <dublinCore> metadata
    4. Extract the effective date from <form><action><action-date>
    5. Extract sponsor information via the congress.gov API
    6. Recursively traverse <legis-body> to store all content in LegislationContent
    """
    init_session()
    with LogContext(
        {
            "bill_number": bill_obj["bill_number"],
            "bill_version": bill_obj["bill_version"],
            "bill_chamber": bill_obj["chamber"],
        }
    ):
        new_bill_version = None
        start_time = time.time()
        res = []
        session = Session()
        congress_id = get_congress_from_session_number(
            int(bill_obj["congress_session"]), session
        )
        try:
            # Parse the raw XML string into an element tree
            root: Element = etree.fromstring(f)
            found = check_for_existing_legislation_version(bill_obj)
            if found:
                logging.info(f"Skipping {archive_obj.get('file')}")
                if found.effective_date is None:
                    logging.info("Missing effective date, re-parsing")
                    # Certain bill versions use <action-date date="..."> while
                    # others use <date>text</date> — try both XPath patterns
                    form_dates = root.xpath("//form/action/action-date") + root.xpath("//form/action/date")
                    if len(form_dates) > 0:
                        last_date = form_dates[-1]
                        try:
                            found.effective_date = parser.parse(
                                last_date.get("date")
                            )
                        except:
                            try:
                                found.effective_date = parser.parse(last_date.text)
                            except:
                                logging.error("Unable to parse date")
                    session.commit()
                    session.flush()
                return []

            
            try:
                title = root.xpath("//dublinCore")[0][0].text
                if ":" in title:
                    title = title.split(":")[-1].strip()
            except:
                logging.error("Couldn't parse title")
                title = "Could not find"

            logging.info(title)
            try:
                new_bill, new_bill_version = find_or_create_bill(
                    bill_obj, title, session
                )
            except sqlalchemy.exc.IntegrityError as e:
                logging.error("Caught IntegrityError, retrying")
                session.rollback()
                time.sleep(1)
                new_bill, new_bill_version = find_or_create_bill(
                    bill_obj, title, session
                )

            session.commit()

            new_vers_id = new_bill_version.version_id
            logging.debug(f"New bill has id {new_vers_id}")
            form_dates = root.xpath("//form/action/action-date") + root.xpath("//form/action/date")
            if len(form_dates) > 0:
                last_date = form_dates[-1]
                try:
                    new_bill_version.effective_date = parser.parse(
                        last_date.get("date")
                    )
                except:
                    try:
                        new_bill_version.effective_date = parser.parse(last_date.text)
                    except:
                        logging.error("Unable to parse date")
            form_element = root.xpath("//form")
            if len(form_element) > 0:
                form_element = form_element[0]
            # extract_sponsors_from_form(form_element, new_bill.legislation_id, session)
            extract_sponsors_from_api(
                congress_id,
                bill_obj,
                new_bill.legislation_id,
                session,
            )
            legis = root.xpath("//legis-body")
            if len(legis) > 0:
                legis = legis[0]
            else:
                logging.warning(f"Bill has {len(legis)} legis-bodies")
                return
            session.commit()
            res = recursive_bill_content(
                None,
                legis,
                0,
                new_bill_version.legislation_version_id,
                {},
                path,
                new_vers_id,
                session=session,
            )
            new_bill_version.completed_at = datetime.datetime.now()
            session.commit()
            end_time = time.time()
            logging.info(
                "Finished parsing bill",
                extra={"bill_parse_duration": end_time - start_time},
            )
        except Exception as e:
            logging.error("Uncaught exception", exc_info=e)
        finally:
            try:
                session.close()
            except:
                pass
        for r in res:
            if "text_element" in r:
                del r["text_element"]
            if "next" in r:
                del r["next"]

        return new_bill_version, res


def open_usc(title):
    """
    Opens a US Code XML file for the given title number and builds a lookup
    dictionary mapping USC identifiers (e.g. "/us/usc/t42/s1395") to their
    corresponding lxml Elements. This enables O(1) lookups when resolving
    cross-references from bill amendment actions.
    """
    lookup = {}
    with open("usc/usc{}.xml".format(title), "rb") as file:
        usc_root = etree.fromstring(file.read())
        lookup["root"] = usc_root
        ids = usc_root.xpath("//*[@identifier]")
        for id in ids:
            lookup[id.attrib["identifier"]] = id
    return lookup


parent_cites = {}


def recursive_get_context(enb):
    # Go up the parent chain till we get a parsed cite
    parent = parent_cites.get(enb, None)
    if parent is None:
        return None
    if parent.get("parsed_cite", "") != "":
        return parent.get("parsed_cite", None)
    if (
        parent.get("parent", "") in parent_cites
        and parent_cites.get(parent.get("parent", "")) != enb
    ):
        return recursive_get_context(parent.get("parent", None))
    return None


last_title = None


def ensure_congress(congress_number: int) -> None:
    """
    Ensures that a congress for the given session exists.

    If we ever want to differentiate between which session of a particular
    congress a bill is in, we'll need to update this schema.

    https://www.senate.gov/legislative/DatesofSessionsofCongress.htm

    Args:
        congress_number (int): [description]
    """
    global EXISTING_CONGRESS, CURRENT_CONGRESS

    # First time it is called, there won't be anything, so we need to ask the DB
    # for the current set of congress sessions we've loaded previously
    if EXISTING_CONGRESS == {}:
        session = Session()
        existings = session.query(Congress).all()
        EXISTING_CONGRESS = {x.session_number: x.congress_id for x in existings}
        session.close()

    if congress_number not in EXISTING_CONGRESS:
        session = Session()
        offset = congress_number - 116
        start_year = 2019 + (offset * 2)
        end_year = start_year + 2
        new_congress = Congress(
            session_number=congress_number, start_year=start_year, end_year=end_year
        )
        session.add(new_congress)
        session.flush()
        session.commit()
        EXISTING_CONGRESS[congress_number] = new_congress.congress_id

    CURRENT_CONGRESS = EXISTING_CONGRESS[congress_number]


def parse_archive(
    path: str,
    chamber_filter: str = None,
    version_filter: str = None,
    number_filter: str = None,
) -> List[LegislationVersion]:
    """
    Opens a ZipFile that is the dump of all bills.
    It will parse each one and return a list of the parsed out objects

    Args:
        path (str):Path to the zip file

    Returns:
        List[Legislation]: List of the parsed objects
    """
    global BASE_VERSION
    session = Session()
    # Get latest release version for the base
    # TODO: Move these around to select the correct release point given the bill
    release_point = (
        session.query(USCRelease).order_by(desc(USCRelease.created_at)).limit(1).all()
    )
    BASE_VERSION = release_point[0].version_id
    print("Base version is", BASE_VERSION)
    print("reee")
    archive = ZipFile(path)
    names = []
    rec = []
    for file in archive.namelist():
        try:
            parsed = filename_regex.search(file)
            house = parsed.group("house")
            session = parsed.group("session")
            bill_number = int(parsed.group("bill_number"))
            bill_version = parsed.group("bill_version")
            file_title = f"{session} - {house}{bill_number} - {bill_version}"
            names.append(
                {
                    "title": file_title,
                    "path": file,
                    "bill_number": bill_number,
                    "bill_version": bill_version,
                    "chamber": chamb[house],
                }
            )
        except Exception as e:
            raise e
            pass

    names = sorted(names, key=lambda x: x["bill_number"])
    print(names)
    # names = names[50:55]
    # names = [x for x in names if (x.get('bill_version') == 'enr')]

    def filter_logic(x):
        if chamber_filter is not None and x["chamber"] != chamber_filter:
            return False

        if version_filter is not None and x["bill_version"] != version_filter:
            return False

        if number_filter is not None and str(x["bill_number"]) != str(number_filter):
            return False

        return True

    names = [x for x in names if filter_logic(x)]
    frec = Parallel(n_jobs=THREADS, backend="multiprocessing", verbose=5)(
        delayed(load_bill)(
            archive.open(name["path"], "r").read().decode(),
            str(name["bill_number"]),
            name,
            {"archive": path.split("/")[-1], "file": name["path"].split("/")[-1]},
        )
        for name in names
    )
    for r in frec:
        rec.extend(r)

    return rec


def parse_archives(
    paths: List[str],
    chamber_filter: str = None,
    version_filter: str = None,
    number_filter: str = None,
) -> List[dict]:
    """
    Opens a series of Zipfiles that is the dump of all bills.
    It will parse each one and return a list of the parsed out objects

    Args:
        path (str):Path to the zip file

    Returns:
        List[dict]: List of the parsed objects
    """
    global BASE_VERSION
    session = Session()
    # Get latest release version for the base
    # TODO: Move these around to select the correct release point given the bill
    names: List[Dict[str, Any]] = []
    rec = []
    open_archives = []
    arch_ind = 0
    for path in paths:
        archive = ZipFile(path)
        open_archives.append(archive)
        for file in archive.namelist():
            try:
                parsed = filename_regex.search(file)
                if parsed is None:
                    print(file, "bad")
                    continue
                house = parsed.group("house")
                congress_session = parsed.group("session")
                bill_number = int(parsed.group("bill_number"))
                bill_version = parsed.group("bill_version")
                file_title = (
                    f"{congress_session} - {house}{bill_number} - {bill_version}"
                )
                names.append(
                    {
                        "title": file_title,
                        "path": file,
                        "bill_number": bill_number,
                        "bill_version": LegislationVersionEnum.from_string(
                            bill_version
                        ),
                        "chamber": LegislationChamber.from_string(chamb[house]),
                        "archive_index": arch_ind,
                        "congress_session": congress_session,
                    }
                )
            except Exception as e:
                print("Error parsing", file)
                print(e)
        arch_ind += 1

    names = sorted(names, key=lambda x: x["bill_number"])
    # names = names[50:55]
    # names = [x for x in names if (x.get('bill_version') == 'enr')]
    print("Names", len(names))
    def filter_logic(x):
        if chamber_filter is not None and x["chamber"] != chamber_filter:
            return False

        if version_filter is not None and x["bill_version"] != version_filter:
            return False

        if number_filter is not None and str(x["bill_number"]) != str(number_filter):
            return False

        return True

    existing_legislation = retrieve_existing_legislations(session)
    print("Existing legislation", len(existing_legislation))
    legis_lookup: Dict[LegislationChamber, List[LegislationVersionEnum]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    for leg in existing_legislation:
        legis_lookup[LegislationChamber(leg["chamber"])][leg["bill_number"]][
            leg["congress_session"]
        ].append(LegislationVersionEnum(leg["bill_version"]))

    def filter_existing_legislation(x):
        return True
        if x["chamber"] in legis_lookup:
            if (
                LegislationVersionEnum(x["bill_version"])
                in legis_lookup[x["chamber"]][x["bill_number"]][x["congress_session"]]
            ):
                return False
        return True

    # names = [x for x in names if filter_logic(x) and filter_existing_legislation(x)]
    print("New legislation hmm", len(names))

    frec = Parallel(n_jobs=THREADS, backend="loky", verbose=5)(
        delayed(parse_bill)(
            open_archives[name["archive_index"]]
            .open(name["path"], "r")
            .read()
            .decode(),
            str(name["bill_number"]),
            name,
            {"archive": path.split("/")[-1], "file": name["path"].split("/")[-1]},
        )
        for name in names
    )
    for r in frec:
        if r is not None:
            rec.extend(r)

    return rec


def run_archives():
    global BASE_VERSION
    session = Session()
    # Get latest release version for the base
    # TODO: Move these around to select the correct release point given the bill
    release_point = (
        session.query(USCRelease)
        .order_by(desc(USCRelease.effective_date))
        .limit(1)
        .all()
    )
    BASE_VERSION = release_point[0].version_id
    print("Base version is", BASE_VERSION)
    rec = parse_archive("bills/116/hr_1.zip")
    rec = rec + parse_archive("bills/116/s_1.zip")
    # df = pandas.DataFrame.from_records(rec)
    # # df.drop('text_element', inplace=True)
    # df.replace({"\u8211": "-", "\u8212": "-"}, inplace=True)
    # os.makedirs("reports", exist_ok=True)
    # df.to_csv("reports/out_{}.csv".format(time.strftime("%d-%m-%Y_%H-%M")), index=False)


if __name__ == "__main__":
    run_archives()

# files = os.listdir('bills')
# #files = ['hr41.xml', 'hr64.xml']
# files = ['hr33.xml']
# rec = []
# for file in files:
#     uscs = {}
#     try:
#         frec = parse_bill(f'bills/{file}')
#         for rr in frec:
#             rr['file'] = file
#         rec.extend(frec)
#     except Exception as e:
#         exc_type, exc_obj, exc_tb = sys.exc_info()
#         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#         print(exc_type, fname, exc_tb.tb_lineno)
#     session = Session()
#     version = Version(
#         base_id=1,
#         title=file
#     )
#     session.add(version)
#     session.flush()
#     session.commit()
#     for action in frec:
#         if(len(action['action']) == 1):
#             run_action(action, version)
#     session.close()

# df = pandas.DataFrame.from_records(rec)
# #df.drop('text_element', inplace=True)
# df.to_csv('out.csv', index=False)
