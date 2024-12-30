from billparser.actions import determine_action
from billparser.run_through import convert_to_text
from billparser.utils.cite_parser import parse_action_for_cite, parse_text_for_cite
from flask_sqlalchemy_session import current_session
import logging

from collections import defaultdict
from typing import Dict, List
from billparser.db.models import LegislationContent, LegislationActionParse
from billparser.db.queries import get_bill_contents


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


def apply_action(
    content_by_parent_id: Dict[int, List[LegislationContent]],
    action: LegislationActionParse,
):
    """
    Applies the action to the database
    """
    pass


def recursively_extract_actions(
    content_by_parent_id: Dict[int, List[LegislationContent]],
    content: LegislationContent,
):
    # Check if the content is a quote block

    if content.content_type == "quote-block":
        # Quotes are separate entities than the action that they come from
        # For our purposes, the quote insertion happens on the tag that the quote is attached to
        return

    if content.content_str is not None and content.content_str.strip() != "":
        # If it has content, then we can extract actions from it
        action_dict = determine_action(content.content_str)
        cite_list = parse_text_for_cite(content.content_str)
        new_action = LegislationActionParse(
            legislation_content_id=content.legislation_content_id,
            legislation_version_id=content.legislation_version_id,
            actions=[action_dict],
            citations=cite_list,
        )
        current_session.add(new_action)
        apply_action(content_by_parent_id, new_action)

    # Continue to recurse
    for child in content_by_parent_id[content.legislation_content_id]:
        recursively_extract_actions(content_by_parent_id, child)


def parse_bill_for_actions(legislation_version_id: int):
    # Inside a transaction, we will generate all of the actions for a bill

    with current_session.begin():
        # Retrieve all the content for the legislation version
        contents = get_bill_contents(legislation_version_id)

        # Put into a dict by parent
        # This will constitute our traversal of the tree
        content_by_parent_id: Dict[int, List[LegislationContent]] = defaultdict(list)
        for content in contents:
            content_by_parent_id[content.parent_id].append(content)

        root_content = content_by_parent_id[None]
