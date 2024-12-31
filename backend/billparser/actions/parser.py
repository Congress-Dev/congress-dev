from billparser.actions import determine_action
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
from billparser.db.models import LegislationContent, LegislationActionParse

PARSER_SESSION = None


def get_bill_contents(legislation_version_id: int) -> List[LegislationContent]:
    query = select(LegislationContent).where(
        LegislationContent.legislation_version_id == legislation_version_id
    )
    results = PARSER_SESSION.execute(query).all()
    # Unpack the results
    return [x[0] for x in results]


def apply_action(
    content_by_parent_id: Dict[int, List[LegislationContent]],
    action: LegislationActionParse,
    parent_actions: List[LegislationActionParse],
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
                        computed_citation = parent_cite["cite"] + "/" + cite["cite"]
                        break
    if computed_citation is None:
        logging.error("No citation found for action")
        return
    if not computed_citation.startswith("/us"):
        logging.error(f"Citation is not complete? {computed_citation=}")
        return
    logging.info(f"Applying action to {computed_citation=}")


def recursively_extract_actions(
    content_by_parent_id: Dict[int, List[LegislationContent]],
    content: LegislationContent,
    parent_actions: List[LegislationActionParse] = [],
):
    # Check if the content is a quote block

    if content.content_type == "quote-block":
        # Quotes are separate entities than the action that they come from
        # For our purposes, the quote insertion happens on the tag that the quote is attached to
        return
    new_action = None

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
        PARSER_SESSION.add(new_action)
        apply_action(content_by_parent_id, new_action, parent_actions)
        new_parents = [*parent_actions] + [new_action]
    else:
        new_parents = parent_actions

    # Continue to recurse
    for child in content_by_parent_id[content.legislation_content_id]:
        recursively_extract_actions(content_by_parent_id, child, new_parents)


def parse_bill_for_actions(legislation_version_id: int):
    # Inside a transaction, we will generate all of the actions for a bill

    with PARSER_SESSION.begin():
        # Retrieve all the content for the legislation version
        contents = get_bill_contents(legislation_version_id)

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
            recursively_extract_actions(content_by_parent_id, content)

        PARSER_SESSION.rollback()
