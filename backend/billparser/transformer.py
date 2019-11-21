from billparser.db.models import Chapter, Section, Content, ContentDiff, Version
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from billparser.db.handler import Session


def recursive_content(
    session,
    chapter_id,
    section_id,
    content_id,
    search_element,
    order,
    version_id,
    last_ident,
):
    # if it has an id it is probably a thingy
    if "id" in search_element.attrib:
        enum = search_element[0]
        ident = last_ident + "/" + enum.attrib["value"]
        heading = search_element[1]
        content_str = None
        if len(search_element) > 2:
            content_elem = search_element[2]
            if (
                "content" in content_elem.tag
                or "chapeau" in content_elem.tag
                or "notes" in content_elem.tag
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
            number=enum.attrib["value"],
            section_display=enum.text,
            content_str=content_str,
            heading=heading.text if heading is not None else None,
        )
        session.add(diff)

        order = 0
        for elem in search_element:
            if "id" in elem.attrib:
                recursive_content(
                    session,
                    chapter_id,
                    section_id,
                    content.content_id,
                    elem,
                    order,
                    version_id,
                    ident,
                )
                order = order + 1


def append_to_end(
    chapter_id, version, section_id, content_id, search_element, order, ident
):
    session = Session()
    recursive_content(
        session,
        chapter_id,
        section_id,
        content_id,
        search_element,
        order,
        version.version_id,
        ident,
    )
    session.commit()
    session.close()


def handle_text_insert(chapter_id, version, section_id, content, text_element, ident):
    # Hmmmmmmm
    session = Session()
    if len(text_element) == 2:
        if "by inserting" in text_element.text:
            to_insert = text_element[0].text.strip()
            if text_element[0].tail.strip() == "after":
                after_text = text_element[1].text.strip()
                print("Inserting", to_insert, "after", after_text)
                if content.content_str is not None:
                    if after_text in content.content_str:
                        print("found")
                    altered = content.content_str.replace(
                        after_text, after_text + " " + to_insert
                    )
                    print(altered)
                    diff = ContentDiff(
                        chapter_id=chapter_id,
                        version_id=version.version_id,
                        content_id=content.content_id,
                        section_id=section_id,
                        content_str=altered,
                    )
                    session.add(diff)
                elif content.heading is not None:
                    if after_text in content.heading:
                        print("found")
                    altered = content.heading.replace(
                        after_text, after_text + " " + to_insert
                    )
                    print(altered)
                    diff = ContentDiff(
                        chapter_id=chapter_id,
                        version_id=version.version_id,
                        content_id=content.content_id,
                        section_id=section_id,
                        heading=altered,
                    )
                    session.add(diff)
    session.commit()
    session.close()


# TODO: Handle multiple updates to the same blob
def handle_text_replace(chapter_id, version, section_id, content, text_element, ident):
    print("Handle text replace")
    print(len(text_element))
    print(text_element.text)
    session = Session()
    if len(text_element) == 2:
        print(text_element.text)
        print(text_element[0].text, text_element[0].tail.strip())
        print(text_element[1].text, text_element[1].tail.strip())
        if "by striking" in text_element.text:
            to_strike = text_element[0].text.strip()
            if text_element[0].tail.strip() == "and inserting":
                replace_with = text_element[1].text.strip()
            else:
                replace_with = ""
            print("Inserting", to_strike, "after", replace_with)
            if content.content_str is not None:
                if to_strike in content.content_str:
                    print("found")
                altered = content.content_str.replace(to_strike, replace_with)
                print(altered)
                diff = ContentDiff(
                    chapter_id=chapter_id,
                    version_id=version.version_id,
                    content_id=content.content_id,
                    section_id=section_id,
                    content_str=altered,
                )
                session.add(diff)
            elif content.heading is not None:
                if to_strike in content.heading:
                    print("found")
                altered = content.heading.replace(to_strike, replace_with)
                print(altered)
                diff = ContentDiff(
                    chapter_id=chapter_id,
                    version_id=version.version_id,
                    content_id=content.content_id,
                    section_id=section_id,
                    heading=altered,
                )
                session.add(diff)
    elif len(text_element) == 1:
        if "by striking" in text_element.text:
            to_strike = text_element[0].text.strip()
            if content.content_str is not None:
                if to_strike in content.content_str:
                    print("found")
                altered = content.content_str.replace(to_strike, "")
                print(altered)
                diff = ContentDiff(
                    chapter_id=chapter_id,
                    version_id=version.version_id,
                    content_id=content.content_id,
                    section_id=section_id,
                    content_str=altered,
                )
                session.add(diff)
            elif content.heading is not None:
                if to_strike in content.heading:
                    print("found")
                altered = content.heading.replace(to_strike, "")
                print(altered)
                diff = ContentDiff(
                    chapter_id=chapter_id,
                    version_id=version.version_id,
                    content_id=content.content_id,
                    section_id=section_id,
                    heading=altered,
                )
                session.add(diff)
    session.commit()
    session.close()


# Target - The element we want to put in
# location - The element we are adding as a sibling to
def insert_after_element(target, location):
    par = location.getparent()
    par.insert(par.index(location) + 1, target)


def strike_text(target, text):
    target.text = target.text.replace(text, "")
