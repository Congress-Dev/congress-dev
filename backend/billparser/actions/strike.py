from billparser.db.handler import Session
from billparser.db.models import USCContentDiff, USCSection, USCContent
from billparser.logger import log
import re
from billparser.actions import ActionObject


def strike_section(action_obj: ActionObject, session: "Session") -> None:
    """
    This handles removing an entire section it does this by making a ContentDiff with empty
    strings for all the parts.

    Args:
        action_obj (ActionObject): Parsed action object
        session (Session): Current database session
    """
    action = action_obj.action
    legislation_content = action_obj.legislation_content
    if legislation_content is not None:
        legislation_id = legislation_content.legislation_content_id
    else:
        legislation_id = None
    new_vers_id = action_obj.version_id
    cited_content = action_obj.cited_content
    """Recursively looks for all contents and marks them as deleted"""
    chapter = (
        session.query(USCSection)
        .filter(USCSection.usc_section_id == cited_content.usc_section_id)
        .limit(1)
        .all()
    )
    if len(chapter) > 0:
        chapter_id = chapter[0].usc_chapter_id
        children = (
            session.query(USCContent)
            .filter(USCContent.usc_ident.like(cited_content.usc_ident + "%"))
            .all()
        )
        log.debug("Found", len(children), "children")
        for child in children:
            diff = USCContentDiff(
                usc_content_id=child.usc_content_id,
                usc_section_id=cited_content.usc_section_id,
                usc_chapter_id=chapter_id,
                version_id=new_vers_id,
                section_display="",
                heading="",
                content_str="",
                legislation_content_id=legislation_id,
            )
            session.add(diff)
    session.commit()


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
    if "$" not in to_strike:
        return re.sub(
            r"{}({})(?:\s|\b)".format(start_boi, re.escape(to_strike)),
            to_replace,
            target,
        )
    elif to_strike in target:
        return target.replace(to_strike, to_replace)
    return target


def strike_text(action_obj: ActionObject, session: "Session") -> None:
    """
    Handle striking and replacing text from a given clause or header.
    It checks to see if the text is within the header or the content, but not both

    TODO: Do both?

    TODO: Return something instead of acting directly on the session

    Args:
        action_obj (ActionObject): Parsed action object
        session (Session): Current DB session
    """
    action = action_obj.action
    cited_content = action_obj.cited_content
    new_vers_id = action_obj.version_id
    legislation_content = action_obj.legislation_content
    if legislation_content is not None:
        legislation_id = legislation_content.legislation_content_id
    else:
        legislation_id = None
    to_strike = action.get("to_remove_text", None)
    to_replace = action.get("to_replace", "")
    chapter = (
        session.query(USCSection)
        .filter(USCSection.usc_section_id == cited_content.usc_section_id)
        .limit(1)
        .all()
    )
    diff = None
    if len(chapter) > 0:
        chapter_id = chapter[0].usc_chapter_id
        if to_strike is not None:
            if cited_content.heading is not None and to_strike in cited_content.heading:
                heading_diff = strike_emulation(
                    to_strike, to_replace, cited_content.heading
                )
                if heading_diff != cited_content.heading:
                    diff = USCContentDiff(
                        usc_content_id=cited_content.usc_content_id,
                        usc_section_id=cited_content.usc_section_id,
                        usc_chapter_id=chapter_id,
                        version_id=new_vers_id,
                        heading=heading_diff,
                        legislation_content_id=legislation_id,
                    )
            elif (
                cited_content.content_str is not None
                and to_strike in cited_content.content_str
            ):
                content_diff = strike_emulation(
                    to_strike, to_replace, cited_content.content_str
                )
                if content_diff != cited_content.content_str:
                    diff = USCContentDiff(
                        usc_content_id=cited_content.usc_content_id,
                        usc_section_id=cited_content.usc_section_id,
                        usc_chapter_id=chapter_id,
                        version_id=new_vers_id,
                        content_str=content_diff,
                        legislation_content_id=legislation_id,
                    )
    if diff is not None:
        session.add(diff)
        session.commit()
    pass
