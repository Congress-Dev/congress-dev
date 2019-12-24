from billparser.transformer import Session
from billparser.translater import translate_paragraph

from billparser.db.models import ContentDiff, Section, Content

from billparser.actions import ActionObject

from billparser.actions.strike import strike_text
import re

from billparser.logger import log

from lxml import etree

Element = etree.Element


def recursive_content(
    chapter_id: int,
    section_id: int,
    content_id: int,
    search_element: Element,
    order: int,
    version_id: int,
    last_ident: str,
    session: "Session",
) -> None:
    """
    This is the function that "inserts" a new block of content from a bill.
    In the case where a bill says "insert blah blah after section E", this will
    recursively look at the content to be inserted, and insert it as a ContentDiff object
    it will also make an empty Content row at the locations, together these signify that
    they have been inserted.

    TODO: Fix this so we aren't having to flush between subsequent calls? We should be able to just assume the new ID, even in parallel circumstances


    Args:
        chapter_id (int): PK in the Chapter table for where this will be inserted
        section_id (int): PK in the Section table for where this will be inserted
        content_id (int): PK of the _parent_ Content for these to be added under
        search_element (Element): The xml element from the bill
        order (int): What order should it be rendered in, this is important because it would be complicated to take the section header and get the order from it
        version_id (int): PK in the Version table, this is the bill's corresponding version
        last_ident (str): This represents the cite location for the newly added content
        session (Session): DB session to add these new objects too
    """
    # if it has an id it is probably an element that we care about
    if "id" in search_element.attrib:

        enum = search_element[0]
        ident = last_ident + "/" + enum.attrib.get("value", "")
        ident = ident.replace("//", "/")
        heading = search_element[1]
        content_str = None

        # TODO: Remember why I had to break this out like this?
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


def insert_section_after(action_obj: ActionObject, session: "Session") -> None:
    """
    Figures out what Chapter/Section we are in so that we can insert after it

    Args:
        action_obj (ActionObject): The parsed action
        session (Session): DB session to insert into
    """
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


def insert_end(action_obj: ActionObject, session: "Session") -> None:
    """
    When an amendment is "insert the following after Section 3(a)"
    This figures out what the latest section is in there and then calls insert after

    Args:
        action_obj (ActionObject): Parsed action
        session ([type]): DB session
    """
    cited_content = action_obj.cited_content
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
            # DRY :)
            insert_section_after(action_obj, session)
        else:
            log.warn("Couldn't find content")


def insert_text_end(action_obj: ActionObject, session: "Session") -> None:
    """
    This is usually called when they want to add text to the end of a single clause

    Args:
        action_obj (ActionObject): Parsed action
        session ([type]): DB session
    """
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


def insert_text_after(action_obj: ActionObject, session: "Session") -> None:
    """
    This typically gets called when they want to add text after another bit of text
    "add 'blah' after 'blibbilty' in Section 3(a) of USC 3"

    TODO: I think I messed up, by calling the strike_text function it may happen more than once?

    Args:
        action_obj (ActionObject): Parsed action
        session ([type]): DB session
    """
    action_obj.action["to_replace"] = (
        action_obj.action["to_remove_text"] + " " + action_obj.action["to_insert_text"]
    )
    strike_text(action_obj, session)


def insert_text_before(action_obj: ActionObject, session: "Session") -> None:
    """
    This typically gets called when they want to add text before another bit of text
    "add 'blah' before 'blibbilty' in Section 3(a) of USC 3"

    TODO: I think I messed up, by calling the strike_text function it may happen more than once?

    Args:
        action_obj (ActionObject): Parsed action
        session ([type]): DB session
    """
    action_obj.action["to_remove_text"] = action_obj.action["target_text"]
    action_obj.action["to_replace"] = (
        action_obj.action["to_insert_text"] + " " + action_obj.action["target_text"]
    )
    strike_text(action_obj, session)
