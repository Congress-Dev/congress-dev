from billparser.transformer import Session
from billparser.db.models import ContentDiff, Section, Content
from billparser.logger import log
import re


def strike_section(action_obj, session):
    action = action_obj.action
    new_vers_id = action_obj.version_id
    cited_content = action_obj.cited_content
    """Recursively looks for all contents and marks them as deleted"""
    chapter = (
        session.query(Section)
        .filter(Section.section_id == cited_content.section_id)
        .limit(1)
        .all()
    )
    if len(chapter) > 0:
        chapter_id = chapter[0].chapter_id
        children = (
            session.query(Content)
            .filter(Content.usc_ident.like(cited_content.usc_ident + "%"))
            .all()
        )
        log.debug("Found", len(children), "children")
        for child in children:
            diff = ContentDiff(
                content_id=child.content_id,
                section_id=cited_content.section_id,
                chapter_id=chapter_id,
                version_id=new_vers_id,
                section_display="",
                heading="",
                content_str="",
            )
            session.add(diff)
    session.commit()


def strike_emu(to_strike, to_replace, target):
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


def strike_text(action_obj, session):
    action = action_obj.action
    cited_content = action_obj.cited_content
    new_vers_id = action_obj.version_id
    to_strike = action.get("to_remove_text", None)
    to_replace = action.get("to_replace", "")
    sub = re.compile(f"\b{re.escape(to_strike)}\b")
    chapter = (
        session.query(Section)
        .filter(Section.section_id == cited_content.section_id)
        .limit(1)
        .all()
    )
    diff = None
    if len(chapter) > 0:
        chapter_id = chapter[0].chapter_id
        if to_strike is not None:
            if cited_content.heading is not None and to_strike in cited_content.heading:
                heading_diff = strike_emu(to_strike, to_replace, cited_content.heading)
                if heading_diff != cited_content.heading:
                    diff = ContentDiff(
                        content_id=cited_content.content_id,
                        section_id=cited_content.section_id,
                        chapter_id=chapter_id,
                        version_id=new_vers_id,
                        heading=heading_diff,
                    )
            elif (
                cited_content.content_str is not None
                and to_strike in cited_content.content_str
            ):
                content_diff = strike_emu(
                    to_strike, to_replace, cited_content.content_str
                )
                if content_diff != cited_content.content_str:
                    diff = ContentDiff(
                        content_id=cited_content.content_id,
                        section_id=cited_content.section_id,
                        chapter_id=chapter_id,
                        version_id=new_vers_id,
                        content_str=content_diff,
                    )
    if diff is not None:
        session.add(diff)
        session.commit()
    pass
