import re
from billparser.utils.logger import LogContext
from billparser.actions import ActionObject, ActionType, determine_action
from billparser.run_through import convert_to_text
from billparser.utils.cite_parser import (
    CiteObject,
    parse_action_for_cite,
    parse_text_for_cite,
)
from billparser.db.handler import Session, get_scoped_session, init_session

from sqlalchemy import select
from sqlalchemy.orm import aliased
from sqlalchemy.sql import func

import logging

from collections import defaultdict
from typing import Dict, List, Optional, Tuple
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
    start_boi = r"(\b)"
    # target = remove_citations(target)
    if "$" not in to_strike:
        return re.sub(
            r"{}({})(?:\b)".format(start_boi, re.escape(to_strike)),
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
    query = select(USCContent).where(USCContent.usc_ident == citation)
    results = session.execute(query).all()

    if len(results) == 0:
        logging.debug("Could not find content", extra={"usc_ident": citation})
        return []

    content = results[0][0]
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
    return []


def insert_text_end(
    action: ActionObject, citation: str, session: "Session"
) -> List[USCContentDiff]:
    query = select(USCContent).where(USCContent.usc_ident == citation)
    results = session.execute(query).all()

    if len(results) == 0:
        logging.debug("Could not find content", extra={"usc_ident": citation})
        return []

    content = results[0][0]
    to_insert_text: Optional[str] = action.get("to_insert_text")
    if to_insert_text is None:
        logging.debug("No insert text")
        return []

    diff = USCContentDiff(
        usc_content_id=content.usc_content_id,
        usc_section_id=content.usc_section_id,
        usc_chapter_id=get_chapter_id(citation.split("/")[3].replace("t", "")),
    )
    if content.heading:
        # We're modifying the heading
        diff.heading = f"{content.heading} {to_insert_text}"
    elif content.content_str:
        diff.content_str = f"{content.content_str} {to_insert_text}"

    if diff.content_str or diff.heading:
        return [diff]
    return []


def _recursively_insert_content(
    sibling_content: Optional[USCContent],
    parent_content: USCContent,
    content_to_insert: LegislationContent,
    content_by_parent_id: Dict[int, List[LegislationContent]],
    action_parse: LegislationActionParse,
    version_id: int,
    session: "Session",
) -> Tuple[List[USCContent], List[USCContentDiff]]:
    new_content: List[USCContent] = []
    new_diffs: List[USCContentDiff] = []
    # Create the content for ourselves
    # then recursively insert the children, extending the new_content and new_diffs
    new_ident = ""
    non_alpha = r"\W"
    if sibling_content:
        # If the sibling is given, use it's ident, and swap the last part with the new content
        new_ident = f"{sibling_content.usc_ident.rsplit('/', 1)[0]}/{content_to_insert.section_display.replace(non_alpha, '')}"
    else:
        # If there is no sibling, then we are the first child
        new_ident = f"{parent_content.usc_ident}/{content_to_insert.section_display.replace(non_alpha, '')}"

    # Use empty heading/content for now
    # When we create the diffs we add all the content, so the frontend will highlight it correctly
    my_content = USCContent(
        usc_ident=new_ident,
        usc_section_id=parent_content.usc_section_id,
        content_type=content_to_insert.content_type,
        parent_id=parent_content.usc_content_id,
        order_number=0 if sibling_content is None else sibling_content.order_number + 1,
        heading=None,
        content_str=None,
        version_id=version_id,
    )
    session.add(my_content)
    session.flush()
    my_diff = USCContentDiff(
        usc_content_id=my_content.usc_content_id,
        usc_section_id=my_content.usc_section_id,
        usc_chapter_id=get_chapter_id(new_ident.split("/")[3].replace("t", "")),
        heading=content_to_insert.heading,
        content_str=content_to_insert.content_str,
        version_id=version_id,
        section_display=content_to_insert.section_display,
    )
    new_content.append(my_content)
    new_diffs.append(my_diff)

    # Now we need to insert the children
    for child in content_by_parent_id[content_to_insert.legislation_content_id]:
        child_content, child_diffs = _recursively_insert_content(
            None,
            my_content,
            child,
            content_by_parent_id,
            action_parse,
            version_id,
            session,
        )
        new_content.extend(child_content)
        new_diffs.extend(child_diffs)

    return new_content, new_diffs


def insert_section_after(
    parent_content: USCContent,
    action_parse: LegislationActionParse,
    citation: str,
    content_by_parent_id: Dict[int, List[LegislationContent]],
    version_id: int,
    session: "Session",
) -> List[USCContentDiff]:
    """
    Inserts a section after the target content
    It comes from the action object, and the action_parse object
    """
    created_diffs: List[USCContentDiff] = []
    # TODO: Manage multiple versions
    query = select(USCContent).where(USCContent.usc_ident == citation)
    results = session.execute(query).all()

    if len(results) == 0:
        logging.debug("Could not find content", extra={"usc_ident": citation})
        return []
    current_sibling = results[0][0]

    # First we need to find the quote-block, it should be the singular child
    quote_block = content_by_parent_id[action_parse.legislation_content_id]
    assert len(quote_block) == 1, "Should be singular child"
    quote_block = quote_block[0]
    assert (
        quote_block.content_type == "quoted-block"
    ), f"Should actually be a quote block; {quote_block.content_type}"

    # Iterate over all of it's children and generate the USCContent/USCContentDiff for them
    # The first level children are going to need to be children of target_content's parent
    # so we'll do them here
    for child in content_by_parent_id[quote_block.legislation_content_id]:
        contents, diffs = _recursively_insert_content(
            current_sibling,
            parent_content,
            child,
            content_by_parent_id,
            action_parse,
            version_id,
            session,
        )
        # Update the sibling since we have just inserted a new content
        current_sibling = contents[0]
        created_diffs.extend(diffs)
    return created_diffs


def insert_section_end(
    action: ActionObject,
    action_parse: LegislationActionParse,
    citation: str,
    content_by_parent_id: Dict[int, List[LegislationContent]],
    version_id: int,
    session: "Session",
):
    # We assume our target citation is the parent section, so to insert at the end we need to find the last child
    query = select(USCContent).where(USCContent.usc_ident == citation)
    results = session.execute(query).all()
    target_section = results[0][0]
    query = (
        select(USCContent)
        .where(USCContent.parent_id == target_section.usc_content_id)
        .order_by(USCContent.order_number.desc())
        .limit(1)
    )
    results = session.execute(query).all()
    last_content = results[0][0]
    return insert_section_after(
        target_section,
        action_parse,
        last_content.usc_ident,
        content_by_parent_id,
        version_id,
        session,
    )


def strike_section(
    action: ActionObject, citation: str, session: "Session"
) -> List[USCContentDiff]:
    # Create USCContentDiffs with the content_str and heading set to ""
    query = select(USCContent).where(USCContent.usc_ident == citation)
    target_section = session.execute(query).first()[0]
    parent = aliased(USCContent)
    child = aliased(USCContent)

    # Recursive CTE to get all descendants
    cte = (
        select(parent.usc_content_id)
        .where(
            parent.usc_content_id == target_section.usc_content_id
        )  # Replace target_id with the starting USCContent ID
        .cte(name="descendants", recursive=True)
    )

    cte = cte.union_all(
        select(child.usc_content_id).where(child.parent_id == cte.c.usc_content_id)
    )

    # Query to get all descendant IDs
    query = select(cte.c.usc_content_id)
    results = session.execute(query).scalars().all()

    query = select(USCContent).where(USCContent.usc_content_id.in_(results))
    contents = session.execute(query).all()

    return [
        USCContentDiff(
            usc_content_id=x[0].usc_content_id,
            usc_section_id=x[0].usc_section_id,
            usc_chapter_id=get_chapter_id(citation.split("/")[3].replace("t", "")),
            content_str="",
            heading="",
            section_display="",
        )
        for x in contents
    ]


def replace_section(
    action: ActionObject,
    action_parse: LegislationActionParse,
    citation: str,
    content_by_parent_id: Dict[int, List[LegislationContent]],
    version_id: int,
    session: "Session",
) -> List[USCContentDiff]:
    # Strike the existing section, then basically call insert_section_after on it
    # This should create a red x blob, and then a new content blob in the diff view
    diffs: List[USCContentDiff] = []
    diffs.extend(strike_section(action, citation, session))
    query = select(USCContent).where(USCContent.usc_ident == citation)
    target_section = session.execute(query).first()[0]
    diffs.extend(
        insert_section_after(
            target_section,
            action_parse,
            citation,
            content_by_parent_id,
            version_id,
            session,
        )
    )
    return diffs


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
    else:
        for parent_action in parent_actions:
            if parent_action.citations:
                parent_cite = parent_action.citations[0]
                if parent_cite["complete"]:
                    # Merge the citations
                    computed_citation = parent_cite["cite"]
                    break
    if computed_citation is None:
        logging.warning("No citation found for action")
        return
    if not computed_citation.startswith("/us"):
        logging.error(
            f"Citation is not complete? {computed_citation=}",
            extra={"citation": computed_citation},
        )
        return
    logging.debug(f"Applying action to {computed_citation=}")
    actions = action.actions
    diffs: List[USCContentDiff] = []
    for act, act_obj in actions[0].items():
        try:
            if act != ActionType.AMEND_MULTIPLE:
                if act == ActionType.STRIKE_TEXT:
                    diffs.extend(
                        strike_text(act_obj, computed_citation, PARSER_SESSION)
                    )
                elif act == ActionType.INSERT_TEXT_END:
                    diffs.extend(
                        insert_text_end(act_obj, computed_citation, PARSER_SESSION)
                    )
                elif act == ActionType.INSERT_END:
                    diffs.extend(
                        insert_section_end(
                            act_obj,
                            action,
                            computed_citation,
                            content_by_parent_id,
                            version_id,
                            PARSER_SESSION,
                        )
                    )
                elif act == ActionType.STRIKE_SUBSECTION:
                    diffs.extend(
                        strike_section(act_obj, computed_citation, PARSER_SESSION)
                    )
                elif act == ActionType.REPLACE_SECTION:
                    diffs.extend(
                        replace_section(
                            act_obj,
                            action,
                            computed_citation,
                            content_by_parent_id,
                            version_id,
                            PARSER_SESSION,
                        )
                    )
                # print(act_obj)
                # print(computed_citation)
        except:
            logging.exception(f"Unexpected failure while parsing action {act_obj}")
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
    with LogContext(
        {
            "legislation_version": {
                "legislation_content_id": LegislationContent.legislation_content_id
            }
        }
    ):
        # Check if the content is a quote block
        if content.content_type == "quoted-block":
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
                apply_action(
                    content_by_parent_id, new_action, parent_actions, version_id
                )
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
    global PARSER_SESSION
    if PARSER_SESSION is None:
        PARSER_SESSION = get_scoped_session()
    PARSER_SESSION.rollback()
    with LogContext(
        {
            "legislation_version": {
                "legislation_version_id": legislation_version.version_id
            }
        }
    ):
        with PARSER_SESSION.begin():
            # Retrieve all the content for the legislation version
            contents = get_bill_contents(legislation_version.legislation_version_id)

            # Put into a dict by parent
            # This will constitute our traversal of the tree
            content_by_parent_id: Dict[int, List[LegislationContent]] = defaultdict(
                list
            )
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
