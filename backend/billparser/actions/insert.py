from billparser.transformer import Session
from billparser.translater import translate_paragraph

from billparser.db.models import ContentDiff, Section, Content

from billparser.actions.strike import strike_text
import re

from billparser.logger import log


def recursive_content(
    chapter_id,
    section_id,
    content_id,
    search_element,
    order,
    version_id,
    last_ident,
    session,
):
    # print(' '.join(search_element.itertext()).strip().replace('\n', ' '))
    # if it has an id it is probably a thingy
    if "id" in search_element.attrib:

        enum = search_element[0]
        ident = last_ident + "/" + enum.attrib.get("value", "")
        ident = ident.replace("//", "/")
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
                content_str = (
                    " ".join(content_elem.itertext()).strip().replace("\n", " ")
                )
        if "heading" in heading.tag:
            content = Content(
                content_type=search_element.tag,
                usc_ident=ident,
                section_id=section_id,
                parent_id=content_id,
                order_number=order,
                version_id=version_id,
            )
        else:
            content_elem = heading
            if (
                "content" in content_elem.tag
                or "chapeau" in content_elem.tag
                or "notes" in content_elem.tag
                or "text" in content_elem.tag
            ):
                content_str = (
                    " ".join(content_elem.itertext()).strip().replace("\n", " ")
                )
            content = Content(
                content_type=search_element.tag,
                usc_ident=ident,
                section_id=section_id,
                parent_id=content_id,
                order_number=order,
                version_id=version_id,
            )
        session.add(content)
        session.flush()
        diff = ContentDiff(
            chapter_id=chapter_id,
            version_id=version_id,
            content_id=content.content_id,
            section_id=section_id,
            number=enum.attrib.get("value", ""),
            section_display=enum.text,
            content_str=content_str,
            heading=heading.text
            if heading is not None and heading.text != content_str
            else None,
        )
        session.add(diff)
        session.commit()
        order = 0
        for elem in search_element:
            if "id" in elem.attrib:
                recursive_content(
                    chapter_id,
                    section_id,
                    content.content_id,
                    elem,
                    order,
                    version_id,
                    ident,
                    session,
                )
                order = order + 1


def insert_section_after(action_obj, session):
    action = action_obj.action
    cited_content = action_obj.cited_content
    new_vers_id = action_obj.version_id
    if action_obj.next is not None:
        chapter = (
            session.query(Section)
            .filter(Section.section_id == cited_content.section_id)
            .all()
        )
        if len(chapter) > 0:
            chapter_id = chapter[0].chapter_id
            recursive_content(
                chapter_id,
                cited_content.section_id,
                cited_content.parent_id,
                translate_paragraph(action_obj.next)[0],
                cited_content.order_number + 1,
                new_vers_id,
                "/".join(cited_content.usc_ident.split("/")[:-1]),
                session,
            )
            session.commit()


def insert_end(action_obj, session):
    action = action_obj.action
    cited_content = action_obj.cited_content
    new_vers_id = action_obj.version_id
    if action_obj.next is not None:
        last_content = (
            session.query(Content)
            .filter(Content.parent_id == cited_content.content_id)
            .order_by(Content.order_number.desc())
            .limit(1)
            .all()
        )
        if len(last_content) > 0:
            action_obj.cited_content = last_content[0]
            insert_section_after(action_obj, session)
        else:
            log.warn("Couldn't find content")


def insert_text_end(action_obj, session):
    action = action_obj.action
    cited_content = action_obj.cited_content
    log.debug(cited_content.content_id)
    new_vers_id = action_obj.version_id
    to_replace = action.get("to_replace", "")
    chapter = (
        session.query(Section)
        .filter(Section.section_id == cited_content.section_id)
        .limit(1)
        .all()
    )
    diff = None
    if len(chapter) > 0:
        chapter_id = chapter[0].chapter_id
        if cited_content.heading is not None:
            heading_diff = cited_content.heading + " " + to_replace
            if heading_diff != cited_content.heading:
                diff = ContentDiff(
                    content_id=cited_content.content_id,
                    section_id=cited_content.section_id,
                    chapter_id=chapter_id,
                    version_id=new_vers_id,
                    heading=heading_diff,
                )
        elif cited_content.content_str is not None:
            content_diff = cited_content.content_str + " " + to_replace
            if content_diff != cited_content.content_str:
                diff = ContentDiff(
                    content_id=cited_content.content_id,
                    section_id=cited_content.section_id,
                    chapter_id=chapter_id,
                    version_id=new_vers_id,
                    content_str=content_diff,
                )
    if diff is not None:
        log.debug("adding")
        session.add(diff)
        session.commit()
        log.debug("Added diff", diff.diff_id)


def insert_text_after(action_obj, session):
    action = action_obj.action
    cited_content = action_obj.cited_content
    new_vers_id = action_obj.version_id
    action_obj.action["to_replace"] = (
        action_obj.action["to_remove_text"] + " " + action_obj.action["to_insert_text"]
    )
    strike_text(action_obj, session)


def insert_text_before(action_obj, session):
    action = action_obj.action
    cited_content = action_obj.cited_content
    new_vers_id = action_obj.version_id
    action_obj.action["to_remove_text"] = action_obj.action["target_text"]
    action_obj.action["to_replace"] = (
        action_obj.action["to_insert_text"] + " " + action_obj.action["target_text"]
    )
    strike_text(action_obj, session)
