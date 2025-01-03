import re
from billparser.actions import ActionObject, ActionType, determine_action
from billparser.run_through import convert_to_text
from billparser.utils.cite_parser import (
    CiteObject,
    parse_action_for_cite,
    parse_text_for_cite,
)
from billparser.db.handler import Session

from sqlalchemy import select
import logging

from collections import defaultdict
from typing import Dict, List, Optional
from billparser.db.models import (
    LegislationContent,
    LegislationActionParse,
    LegislationVersion,
    USCChapter,
    USCContent,
    USCContentDiff,
)

PARSER_SESSION = None


def get_bill_contents(legislation_version_id: int) -> List[LegislationContent]:
    query = select(LegislationContent).where(
        LegislationContent.legislation_version_id == legislation_version_id
    )
    results = PARSER_SESSION.execute(query).all()
    # Unpack the results
    return [x[0] for x in results]


def strike_emulation(to_strike: str, to_replace: str, target: str) -> str:
    """
    Handles emulating the strike text behavior for a given string

    Args:
        to_strike (str): Text to search for
        to_replace (str): Text to replace with, if any
        target (str): Text to look in

    Returns:
        str: The result of the replacement
    """
    start_boi = r"(\s|\b)"
    if re.match(r"[^\w]", to_strike):
        start_boi = ""
    # target = remove_citations(target)
    if "$" not in to_strike:
        return re.sub(
            r"{}({})(?:\s|\b)".format(start_boi, re.escape(to_strike)),
            to_replace,
            target,
        )
    elif to_strike in target:
        return target.replace(to_strike, to_replace)
    return target


def get_chapter_id(chapter: str) -> int:
    query = select(USCChapter).where(USCChapter.short_title == chapter)
    result = PARSER_SESSION.execute(query).first()[0]
    return result.usc_chapter_id


def strike_text(
    action: ActionObject, citation: str, session: "Session"
) -> List[USCContentDiff]:
    print("Searching for", citation)
    query = select(USCContent).where(USCContent.usc_ident == citation)
    results = session.execute(query).all()
    if len(results) == 0:
        logging.debug("Could not find content", extra={"usc_ident": citation})
        return []
    content = results[0][0]
    print(results)
    print(action)
    to_strike: Optional[str] = action.get("to_remove_text")
    to_replace: Optional[str] = action.get("to_replace")
    if to_strike is None:
        logging.debug("No strike text found")
        return []
    diff = USCContentDiff(
        usc_content_id=content.usc_content_id,
        usc_section_id=content.usc_section_id,
        usc_chapter_id=get_chapter_id(citation.split("/")[3].replace("t", "")),
    )

    if content.heading:
        # We're modifying the heading
        strike_result = strike_emulation(to_strike, to_replace or "", content.heading)
        # If they're different, store it
        if strike_result != content.heading:
            diff.heading = strike_result

    elif content.content_str:
        strike_result = strike_emulation(
            to_strike, to_replace or "", content.content_str
        )
        # If they're different, store it
        if strike_result != content.content_str:
            diff.content_str = strike_result

    if diff.content_str or diff.heading:
        return [diff]


def apply_action(
    content_by_parent_id: Dict[int, List[LegislationContent]],
    action: LegislationActionParse,
    parent_actions: List[LegislationActionParse],
    version_id: int,
):
    """
    Applies the action to the database, we pass in the parent actions so that we can use them for the citations
    that may indicate where the changes need to go.
    """
    computed_citation: Optional[str] = None
    # First we need to construct the citation we intend to go by
    if action.citations:
        cite: CiteObject = action.citations[0]
        if cite["complete"]:
            computed_citation = cite["cite"]
        else:
            # We need to go up the parent chain
            for parent_action in parent_actions:
                if parent_action.citations:
                    parent_cite = parent_action.citations[0]
                    if parent_cite["complete"]:
                        # Merge the citations
                        computed_citation = parent_cite["cite"] + cite["cite"]
                        break
    if computed_citation is None:
        logging.error("No citation found for action")
        return
    if not computed_citation.startswith("/us"):
        logging.error(f"Citation is not complete? {computed_citation=}")
        return
    logging.info(f"Applying action to {computed_citation=}")
    actions = action.actions
    diffs: List[USCContentDiff] = []
    print(actions[0])
    for act, act_obj in actions[0].items():
        if act != ActionType.AMEND_MULTIPLE:
            print(act)
            if act == ActionType.STRIKE_TEXT:
                print("striking")
                diffs.extend(strike_text(act_obj, computed_citation, PARSER_SESSION))
            print(act_obj)
            print(computed_citation)
    for diff in diffs:
        diff.legislation_content_id = action.legislation_content_id
        diff.version_id = version_id
        PARSER_SESSION.add(diff)


def recursively_extract_actions(
    content_by_parent_id: Dict[int, List[LegislationContent]],
    content: LegislationContent,
    parent_actions: List[LegislationActionParse] = [],
    version_id: int = 0,
):
    # Check if the content is a quote block
    if content.content_type == "quote-block":
        # Quotes are separate entities than the action that they come from
        # For our purposes, the quote insertion happens on the tag that the quote is attached to
        return
    new_action = None
    new_parents = []
    if content.content_str is not None and content.content_str.strip() != "":
        # If it has content, then we can extract actions from it
        action_dict = determine_action(content.content_str)
        cite_list = parse_text_for_cite(content.content_str)
        if action_dict != {} or cite_list != []:
            new_action = LegislationActionParse(
                legislation_content_id=content.legislation_content_id,
                legislation_version_id=content.legislation_version_id,
                actions=[action_dict],
                citations=cite_list,
            )
            PARSER_SESSION.add(new_action)
            apply_action(content_by_parent_id, new_action, parent_actions, version_id)
            new_parents = [*parent_actions] + [new_action]
    else:
        new_parents = parent_actions

    # Continue to recurse
    for child in content_by_parent_id[content.legislation_content_id]:
        recursively_extract_actions(
            content_by_parent_id, child, new_parents, version_id
        )


def parse_bill_for_actions(legislation_version: LegislationVersion):
    # Inside a transaction, we will generate all of the actions for a bill

    with PARSER_SESSION.begin():
        # Retrieve all the content for the legislation version
        contents = get_bill_contents(legislation_version.legislation_version_id)

        # Put into a dict by parent
        # This will constitute our traversal of the tree
        content_by_parent_id: Dict[int, List[LegislationContent]] = defaultdict(list)
        for content in contents:
            content_by_parent_id[content.parent_id].append(content)

        # Sort the lists now so we can proceed in a depth first manner
        for parent_id, content_list in content_by_parent_id.items():
            content_list.sort(key=lambda x: x.legislation_content_id)

        root_content = content_by_parent_id[None]

        # Iterate over the root children
        for content in root_content:
            recursively_extract_actions(
                content_by_parent_id, content, [], legislation_version.version_id
            )
        PARSER_SESSION.flush()
        PARSER_SESSION.commit()
