import os
import re
import sys
import time
import traceback
from zipfile import ZipFile
import hashlib
import datetime
import pandas
from lxml import etree
from unidecode import unidecode  # GPLV2

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
    Bill,
    BillContent,
    BillVersion,
    ContentDiff,
    BillIngestion,
)
from billparser.helpers import convert_to_usc_id
from billparser.logger import log
from billparser.transformer import (
    Content,
    Section,
    Session,
    Version,
    append_to_end,
    handle_text_insert,
    handle_text_replace,
    insert_after_element,
)
from billparser.translater import translate_paragraph

from joblib import Parallel, delayed
from typing import List

text_paths = ["legis-body/section/subsection/text", "legis-body/section/text"]

BASE_VERSION = 1
THREADS = int(os.environ.get("PARSE_THREADS", 16))

Element = etree.Element


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
        log.error("{} {} {}".format(exc_type, fname, exc_tb.tb_lineno))
    return res


def extract_single_action(element: Element, path: str, parent_action: dict) -> list:
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
            if element[1].tag == "header" and element[2].tag == "text":
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
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.error("{} {} {}".format(exc_type, fname, exc_tb.tb_lineno))
    if res != {}:
        res["parsed_cite"] = parse_action_for_cite(res).replace("//", "/")
        actions = determine_action2(res["text"])
        res["action"] = list(actions.keys())
        res["action1"] = list(actions.keys())
        res["actions"] = actions
    return res


SecTitleRegex = re.compile(
    r"(?:(?:Subsection|paragraph) \((?P<finalsub>.?)\) of )?Section (?P<section>\d*)(?:\((?P<sub1>.*?)\)(?:\((?P<sub2>.*?)\)(?:\((?P<sub3>.*?)\))?)?)? of title (?P<title>[0-9A]*)",
    re.IGNORECASE,
)

SubSecRegex = re.compile(r"subsection\s\((.)\)", re.IGNORECASE)

SuchTitleRegex = re.compile(
    r"Section (?P<section>\d*)(?:\((?P<sub1>.*?)\)(?:\((?P<sub2>.*?)\)(?:\((?P<sub3>.*?)\))?)?)? of such (title)",
    re.IGNORECASE,
)

cite_contexts = {"last_title": None}


def parse_action_for_cite(action_object: dict) -> str:
    """
    Looks at a given action object to determine what citation it is trying to edit.
    A citation represents a location in the USCode

    # TODO: Split function apart

    Args:
        action_object (dict): An object represented an extract action

    Returns:
        str: A USCode citation str
    """
    try:
        parent_cite = ""
        if action_object["text_element"] is not None:
            xref = action_object["text_element"].find("external-xref[@legal-doc='usc']")
            if xref is not None:
                cite = convert_to_usc_id(xref)
                action_object["cite_parse"] = cite
                cite_contexts[action_object["enum"]] = cite
                if len(cite.split("/")) > 3:
                    cite_contexts["last_title"] = cite.split("/")[3][1:]
                return cite
            if not isinstance(action_object["text_element"].text, str):
                return ""
            text_obj = action_object["text_element"].text.strip()
            SecTitleRegex_match = SecTitleRegex.search(text_obj)
            if SecTitleRegex_match:
                cite = "/us/usc/t{}/s{}".format(
                    SecTitleRegex_match["title"], SecTitleRegex_match["section"]
                )
                possibles = [
                    SecTitleRegex_match[f"sub{x}"]
                    for x in range(1, 3)
                    if SecTitleRegex_match[f"sub{x}"]
                ]
                if SecTitleRegex_match["finalsub"]:
                    possibles.append(SecTitleRegex_match["finalsub"])
                if len(possibles) > 0:
                    cite += "/" + "/".join(possibles)
                cite_contexts[action_object["enum"]] = cite
                cite_split = cite.split("/")
                if len(cite_split) > 3:
                    cite_contexts["last_title"] = cite.split("/")[3][1:]
                return cite
            SuchTitleRegex_match = SuchTitleRegex.search(text_obj)
            if SuchTitleRegex_match:
                cite = "/us/usc/t{}/s{}".format(
                    cite_contexts["last_title"], SuchTitleRegex_match["section"]
                )
                possibles = [
                    SuchTitleRegex_match[f"sub{x}"]
                    for x in range(1, 3)
                    if SuchTitleRegex_match[f"sub{x}"]
                ]
                if len(possibles) > 0:
                    cite += "/" + "/".join(possibles)
                cite_contexts[action_object["enum"]] = cite
                return cite
            if action_object["parent"] in cite_contexts:
                parent_cite = cite_contexts[action_object["parent"]]
            else:
                parent_cite = ""
            SubSecRegex_match = SubSecRegex.search(text_obj)
            if SubSecRegex_match:
                cite = parent_cite + "/" + SubSecRegex_match[1]
                cite_contexts[action_object["enum"]] = cite
                cite_split = cite.split("/")
                if len(cite_split) > 3:
                    cite_contexts["last_title"] = cite_split[3][1:]
                return cite
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        traceback.print_exc()

    return parent_cite


def find_or_create_bill(bill_obj: dict, title: str, session: "SQLAlchemy.session"):
    base = session.query(Version).filter(Version.base_id == None).all()[0]
    bill_row = (
        session.query(Bill)
        .filter(Bill.bill_number == bill_obj["bill_number"])
        .filter(Bill.chamber == bill_obj["chamber"])
        .all()
    )
    if len(bill_row) == 0:
        new_bill = Bill(
            bill_number=bill_obj["bill_number"],
            bill_title=title,
            chamber=bill_obj["chamber"],
            bill_type="Bill",
        )
        session.add(new_bill)
        session.commit()
        new_bill_version = BillVersion(
            bill_id=new_bill.bill_id,
            bill_version=bill_obj["bill_version"],
            base_version_id=base.version_id,
        )
        session.add(new_bill_version)
    else:
        new_bill = bill_row[0]
        version_row = (
            session.query(BillVersion)
            .filter(BillVersion.bill_id == new_bill.bill_id)
            .filter(BillVersion.bill_version == bill_obj["bill_version"])
            .all()
        )
        if len(version_row) == 0:
            new_bill_version = BillVersion(
                bill_id=new_bill.bill_id,
                bill_version=bill_obj["bill_version"],
                base_version_id=base.version_id,
            )
            session.add(new_bill_version)
        else:
            new_bill_version = version_row[0]

    session.commit()
    return (new_bill, new_bill_version)


def clear_existing_content(bill_version, session):
    vers = (
        session.query(Version)
        .filter(Version.bill_version_id == bill_version.bill_version_id)
        .all()
    )
    if len(vers) > 0 and vers[0].version_id != BASE_VERSION:
        log.info("Deleting the old stuff")
        session.query(ContentDiff).filter(
            ContentDiff.version_id == vers[0].version_id
        ).delete()
        session.query(Content).filter(Content.version_id == vers[0].version_id).delete()
        session.query(BillContent).filter(
            BillContent.bill_version_id == bill_version.bill_version_id
        ).delete()
        session.flush()
        session.query(Version).filter(
            Version.bill_version_id == bill_version.bill_version_id
        ).delete()
        session.commit()


def create_version(new_bill_version, title, session):
    new_vers = Version(
        base_id=new_bill_version.base_version_id,
        bill_version_id=new_bill_version.bill_version_id,
        title=title,
    )
    session.add(new_vers)
    session.commit()
    return new_vers.version_id


def recursive_bill_content(
    content_id,
    search_element,
    order,
    version_id,
    parents: dict,
    path,
    vers_id: int,
    parent_cite: str = "",
    session: "SQLAlchemy.session" = None,
) -> list:
    # print(' '.join(search_element.itertext()).strip().replace('\n', ' '))
    # if it has an id it is probably a thingy
    extracted_action = []
    res = []
    if True:
        root_path = search_element.getroottree().getpath(search_element)
        sections = root_path.split("/section")
        if len(sections) > 2:
            pass
        elif "quote" in root_path:
            # print("Within quote")
            pass
        else:
            try:
                temp_actions = [extract_single_action(search_element, path, {})]
                new_acts = []
                res.append(temp_actions[0])
                path = temp_actions[0].get("enum", path)
                for act in temp_actions:
                    if act.get("parsed_cite") is not None:
                        parent_cite = act.get("parsed_cite")
                    chg, act = run_action2(act, None, vers_id, session)
                    for e in act:
                        e["changed"] = chg
                    new_acts.extend(act)

                for e in new_acts:
                    if isinstance(
                        e.get("action", {}).get("text_element"), etree._Element
                    ):
                        e["action"]["text_element"] = e["action"]["text_element"].tag
                    if isinstance(e.get("action", {}).get("next"), etree._Element):
                        e["action"]["next"] = e["action"]["next"].tag
                    extracted_action.append(e)
                # res.extend(extracted_action)
            except Exception as e:
                traceback.print_exc()
                pass
    if (search_element.tag == "legis-body" or "id" in search_element.attrib) and len(
        search_element
    ) > 1:
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
            content = BillContent(
                content_type=search_element.tag,
                parent_id=content_id,
                order_number=order,
                bill_version_id=version_id,
                section_display=enum.text,
                content_str=content_str,
                heading=heading.text if heading is not None else None,
                action_parse=extracted_action,
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
            content = BillContent(
                content_type=search_element.tag,
                parent_id=content_id,
                order_number=order,
                bill_version_id=version_id,
                section_display=enum.text,
                content_str=content_str,
                # heading=heading.text if heading is not None else None,
                action_parse=extracted_action,
            )
        # print(content.to_dict())
        session.add(content)
        session.flush()
        order = 0

        for elem in search_element:
            if "id" in elem.attrib:
                res.extend(
                    recursive_bill_content(
                        content.bill_content_id,
                        elem,
                        order,
                        version_id,
                        parents,
                        path,
                        vers_id,
                        parent_cite,
                        session=session,
                    )
                )
                order = order + 1
    return res


def check_existing_ingestion(checksum: str, archive_obj: object, session) -> bool:
    result = (
        session.query(BillIngestion)
        .filter(
            BillIngestion.archive_name == archive_obj.get("archive"),
            BillIngestion.archive_path == archive_obj.get("file"),
            BillIngestion.checksum == checksum,
            BillIngestion.completed_at != None
        )
        .all()
    )
    return result is None


def parse_bill(f: str, path: str, bill_obj: object, archive_obj: object):
    res = []
    try:
        session = Session()
        m = hashlib.md5()
        m.update(f.encode("utf-8"))
        checksum = m.hexdigest()
        found = check_existing_ingestion(checksum, archive_obj, session)
        if found:
            log.info(f"Skipping {archive_obj.get('path')}")
            return []
        ingestion_row = BillIngestion(
            archive_name = archive_obj.get("archive"),
            archive_path = archive_obj.get("file"),
            checksum = checksum,
        )
        root = etree.fromstring(f)
        title = root.xpath("//dublinCore")[0][0].text.split(":")[-1].strip()
        log.info(title)
        new_bill, new_bill_version = find_or_create_bill(bill_obj, title, session)
        ingestion_row.bill_version_id = new_bill_version.bill_version_id
        session.add(ingestion_row)
        session.commit()
        clear_existing_content(new_bill_version, session)
        new_vers_id = create_version(
            new_bill_version,
            f"{new_bill.chamber} - {new_bill.bill_number} - {new_bill_version.bill_version}",
            session,
        )
        legis = root.xpath("//legis-body")
        if len(legis) > 0:
            legis = legis[0]
        else:
            return
        session.commit()
        res = recursive_bill_content(
            None,
            legis,
            0,
            new_bill_version.bill_version_id,
            {},
            path,
            new_vers_id,
            session=session,
        )
        ingestion_row.completed_at = datetime.datetime.now()
        session.commit()
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        traceback.print_exc()
    for r in res:
        if "text_element" in r:
            del r["text_element"]
        if "next" in r:
            del r["next"]

    return res


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
    actions = ACTION.get("actions", {})
    # print(action)
    # print(actions.keys())
    made_something = False
    existing_diffs = (
        session.query(ContentDiff.diff_id)
        .filter(ContentDiff.version_id == new_vers_id)
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
            )

            action_object.set_action(action)
            ACTION["parsed_cite"] = action_object.parsed_cite
            action_objs.append(action_object.to_dict())
            if action_key == "AMEND-MULTIPLE" or action_object.parsed_cite == "":
                continue

            cited_content = (
                session.query(Content)
                .filter(
                    Content.usc_ident == action_object.parsed_cite,
                    Content.version_id == BASE_VERSION,
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
                log.debug(
                    "Unable to find",
                    len(cited_content),
                    action_object.parsed_cite,
                    BASE_VERSION,
                )
    ending_diff = (
        session.query(ContentDiff.diff_id)
        .filter(ContentDiff.version_id == new_vers_id)
        .count()
    )
    session.flush()
    session.commit()
    # print('=========')
    return (existing_diffs < ending_diff), action_objs


filename_regex = re.compile(
    r"BILLS-(?P<session>\d\d\d)(?P<house>\D+)(?P<bill_number>\d+)(?P<bill_version>\D+)\.xml"
)
chamb = {"hr": "House", "s": "Senate"}


def parse_archive(path: str) -> List[dict]:
    """
    Opens a ZipFile that is the dump of all bills.
    It will parse each one and return a list of the parsed out objects

    Args:
        path (str):Path to the zip file

    Returns:
        List[dict]: List of the parsed objects
    """
    archive = ZipFile(path)
    names = []
    rec = []
    for file in archive.namelist():
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

    names = sorted(names, key=lambda x: x["bill_number"])
    names = names[30:35]
    # names = [x for x in names if (x.get('title') == '116 - hr4 - ih')]
    # names = [x for x in names if (x.get('bill_version') == 'enr')]
    frec = Parallel(n_jobs=THREADS, backend="multiprocessing", verbose=5)(
        delayed(parse_bill)(
            archive.open(name["path"], "r").read().decode(),
            str(name["bill_number"]),
            name,
            {"archive": path.split("/")[-1], "file": file.split("/")[-1]},
        )
        for name in names[:100]
    )
    for r in frec:
        rec.extend(r)

    return rec


def run_archives():
    global BASE_VERSION
    session = Session()
    res = session.query(Version).filter(Version.title == "Q1-2019").limit(1).all()
    BASE_VERSION = res[0].version_id
    print("Base version is", BASE_VERSION)
    rec = parse_archive("bills/116/hr_1.zip")
    rec = rec + parse_archive("bills/116/s_1.zip")
    df = pandas.DataFrame.from_records(rec)
    # df.drop('text_element', inplace=True)
    df.replace({"\u8211": "-", "\u8212": "-"}, inplace=True)
    os.makedirs("reports", exist_ok=True)
    df.to_csv("reports/out_{}.csv".format(time.strftime("%d-%m-%Y_%H-%M")), index=False)


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
