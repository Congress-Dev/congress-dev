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

from billparser.actions import ActionObject
from billparser.actions import determine_action as determine_action2
from billparser.actions.insert import (
    insert_section_after,
    insert_text_after,
    insert_text_before,
    insert_end,
)
from billparser.actions.redesignate import redesignate
from billparser.actions.strike import strike_section, strike_text
from billparser.db.models import (
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
from billparser.metadata.sponsors import (
    extract_sponsors_from_form,
    extract_sponsors_from_api,
)

from billparser.utils.logger import LogContext
from billparser.utils.cite_parser import parse_action_for_cite, ActionObject
from billparser.db.handler import Session, init_session
from billparser.translater import translate_paragraph

from joblib import Parallel, delayed
from typing import Any, Dict, List
from functools import lru_cache

text_paths = ["legis-body/section/subsection/text", "legis-body/section/text"]
filename_regex = re.compile(
    r"BILLS-(?P<session>\d\d\d)(?P<house>\D+)(?P<bill_number>\d+)(?P<bill_version>\D+)\.xml"
)
chamb = {"hr": "House", "s": "Senate"}
BASE_VERSION = 1
EXISTING_CONGRESS = {}
CURRENT_CONGRESS = None
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


ll = {"subsection": "ss", "paragraph": "p", "section": "s", "subparagraph": "sb"}


def extract_actions(element: Element, path: str) -> List[dict]:
    """
    Looks at an element for textual clues to determine what actions it is implying
    These actions will be extracted and passed to other functions to utilize.

    This is a recursive function

    Args:
        element (Element): An XML element from a bill.
        path (str): The path of this element in the document

    Returns:
        List[dict]: A flat list of the extracted actions of all the elements
    """

    res = []
    try:
        # Quoted blocks are usually the "inserty" things
        if "quoted-block" in element.tag:
            return res
        tag_lookup = {}
        for elem in element:
            tag_lookup[elem.tag] = elem
        # 90% sure they all have an enum tag for the first element
        if len(element) > 0 and element[0].tag == "enum" and element.tag in ll:
            spath = "{}/{}{}".format(
                path, ll[element.tag], element[0].text.replace(".", "")
            )
            lxml_path = element.getroottree().getpath(element)
            if element[1].tag == "header" and element[2].tag == "text":
                text = convert_to_text(element[2])
                next_elem = ""
                if len(element) == 4:
                    next_elem = element[3]
                res.append(
                    {
                        "parent": path,
                        "enum": spath,
                        "lxml_path": lxml_path,
                        "text": text,
                        "text_element": element[2],
                        "amended": "amended" in text,
                        "next": next_elem,
                    }
                )
                if len(element) > 3:
                    for elem in element[3:]:
                        res.extend(extract_actions(elem, spath))
            elif element[1].tag == "text":
                text = convert_to_text(element[1])
                next_elem = ""
                if len(element) == 3:
                    next_elem = element[2]
                res.append(
                    {
                        "parent": path,
                        "enum": spath,
                        "lxml_path": lxml_path,
                        "text": text,
                        "text_element": element[1],
                        "amended": "amended" in text,
                        "next": next_elem,
                    }
                )
                if len(element) > 2:
                    for elem in element[2:]:
                        res.extend(extract_actions(elem, spath))
            elif element[2].tag in ["paragraph", "subsection"]:
                for elem in element[2:]:
                    res.extend(extract_actions(elem, spath))
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        logging.error("{} {} {}".format(exc_type, fname, exc_tb.tb_lineno))
    return res


def extract_single_action(
    element: Element, path: str, parent_cite: str
) -> List[ActionObject]:
    """
    Takes in an element and a path (relative within the bill)
    returns a list of extracted actions.
    """
    res = {}
    try:
        # Quoted blocks are usually the "inserty" things
        if "quoted-block" in element.tag:
            return res
        tag_lookup = {}
        for elem in element:
            tag_lookup[elem.tag] = elem
        # 90% sure they all have an enum tag for the first element
        if len(element) > 0 and element[0].tag == "enum" and element.tag in ll:
            spath = "{}/{}{}".format(
                path, ll[element.tag], element[0].text.replace(".", "")
            )
            lxml_path = element.getroottree().getpath(element)
            if element[1].tag == "header" and (
                len(element) > 2 and element[2].tag == "text"
            ):
                text = convert_to_text(element[2])
                next_elem = ""
                if len(element) == 4:
                    next_elem = element[3]
                res = {
                    "parent": path,
                    "enum": spath,
                    "lxml_path": lxml_path,
                    "text": text,
                    "text_element": element[2],
                    "amended": "amended" in text,
                    "next": next_elem,
                }
            elif element[1].tag == "text":
                text = convert_to_text(element[1])
                next_elem = ""
                if len(element) == 3:
                    next_elem = element[2]
                res = {
                    "parent": path,
                    "enum": spath,
                    "lxml_path": lxml_path,
                    "text": text,
                    "text_element": element[1],
                    "amended": "amended" in text,
                    "next": next_elem,
                }
    except Exception as e:
        logging.error("Uncaught exception", exc_info=e)
    if res != {}:
        res["parsed_cite"] = parse_action_for_cite(res).replace("//", "/")
        if res["parsed_cite"] == "/us/usc/t42/s18071/None":
            print("Failure", res)
        actions = determine_action2(res["text"])
        res["action"] = list(actions.keys())
        res["action1"] = list(actions.keys())
        res["actions"] = actions
    return res


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
    new_version = Version(base_id=BASE_VERSION)
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
    # logging.debug(' '.join(search_element.itertext()).strip().replace('\n', ' '))
    # if it has an id it is probably a thingy
    extracted_action = []
    res: List[LegislationContent] = []
    content = None

    if search_element.tag == "legis-body":
        # Root node for us
        content = LegislationContent(
            content_type=search_element.tag,
            parent_id=content_id,
            order_number=order,
            legislation_version_id=legis_version_id,
            section_display=None,
            content_str=None,
        )
    elif ("id" in search_element.attrib) and len(search_element) > 1:
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


def check_for_existing_legislation_version(bill_obj: object) -> bool:
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
    return len(result) > 0


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
        )
        .join(LegislationVersion)
        .all()
    )
    return [
        {
            "chamber": x[0],
            "bill_number": x[1],
            "bill_version": x[2],
        }
        for x in existing_legis
    ]


def parse_bill(
    f: str, path: str, bill_obj: object, archive_obj: object
) -> LegislationVersion:
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
        try:

            found = check_for_existing_legislation_version(bill_obj)
            if found:
                logging.info(f"Skipping {archive_obj.get('file')}")
                return []

            root: Element = etree.fromstring(f)
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
            form_dates = root.xpath("//form/action/action-date")
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
                EXISTING_CONGRESS[int(bill_obj["congress_session"])],
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


def run_action2(ACTION, new_bill_version, new_vers_id, session):
    global last_title
    # First set some linkage to the parent
    parent_cites[ACTION.get("enum", "")] = ACTION
    parsed_cite = ACTION.get("parsed_cite", "")
    if parsed_cite != "":
        last_title = "/".join(parsed_cite.split("/")[:4])
        # print('Last title set to', last_title)
    parent_cite = ""
    if "usc" not in parsed_cite:
        parent_cite = recursive_get_context(ACTION.get("enum", ""))

    # Filter out the financial/date ones for now
    actions = {
        k: v
        for k, v in ACTION.get("actions", {}).items()
        if k not in ["FINANCIAL", "DATE"]
    }
    # print(action)
    # print(actions.keys())
    made_something = False
    existing_diffs = (
        session.query(USCContentDiff.usc_content_diff_id)
        .filter(USCContentDiff.version_id == new_vers_id)
        .count()
    )
    action_objs = []
    if len(actions) == 1 or (len(actions) == 2 and "AMEND-MULTIPLE" in actions):
        for action_key in actions:
            action = actions.get(action_key)
            action_object = ActionObject(
                action_key=action_key,
                parent_cite=parent_cite,
                parsed_cite=parsed_cite,
                version_id=new_vers_id,
                last_title=last_title,
                next=ACTION.get("next", None),
                legislation_content=ACTION.get("legislation_content", None),
            )

            action_object.set_action(action)
            ACTION["parsed_cite"] = action_object.parsed_cite
            action_objs.append(action_object.to_dict())
            if action_key == "AMEND-MULTIPLE" or action_object.parsed_cite == "":
                continue
            cited_content = (
                session.query(USCContent)
                .filter(
                    USCContent.usc_ident == action_object.parsed_cite,
                    USCContent.version_id == BASE_VERSION,
                )
                .all()
            )
            if len(cited_content) == 1:
                action_object.cited_content = cited_content[0]
                if action_key == "STRIKE-SUBSECTION":
                    strike_section(action_object, session)
                elif action_key == "REDESIGNATE":
                    redesignate(action_object, session)
                elif action_key == "STRIKE-TEXT":
                    strike_text(action_object, session)
                elif action_key == "INSERT-SECTION-AFTER":
                    insert_section_after(action_object, session)
                elif action_key == "INSERT-TEXT-AFTER":
                    insert_text_after(action_object, session)
                elif action_key == "REPLACE-SECTION":
                    strike_section(action_object, session)
                    insert_section_after(action_object, session)
                elif action_key == "INSERT-TEXT":
                    insert_text_before(action_object, session)
                elif action_key == "INSERT-END":
                    insert_end(action_object, session)
                elif action_key == "INSERT-TEXT-END":
                    insert_end(action_object, session)
            else:
                logging.debug(
                    "Unable to find",
                    len(cited_content),
                    action_object.parsed_cite,
                    BASE_VERSION,
                )
    ending_diff = (
        session.query(USCContentDiff.usc_content_diff_id)
        .filter(USCContentDiff.version_id == new_vers_id)
        .count()
    )
    session.flush()
    session.commit()
    # print('=========')
    return (existing_diffs < ending_diff), action_objs


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
        except:
            pass

    names = sorted(names, key=lambda x: x["bill_number"])
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
    release_point = (
        session.query(USCRelease).order_by(desc(USCRelease.created_at)).limit(1).all()
    )
    BASE_VERSION = release_point[0].version_id
    print("Base version is", BASE_VERSION)
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
        lambda: defaultdict(list)
    )
    for leg in existing_legislation:
        legis_lookup[LegislationChamber(leg["chamber"])][leg["bill_number"]].append(
            LegislationVersionEnum(leg["bill_version"])
        )

    def filter_existing_legislation(x):
        if x["chamber"] in legis_lookup:
            if (
                LegislationVersionEnum(x["bill_version"])
                in legis_lookup[x["chamber"]][x["bill_number"]]
            ):
                return False
        return True

    names = [x for x in names if filter_logic(x) and filter_existing_legislation(x)]
    print("New legislation", len(names))

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
