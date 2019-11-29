from billparser.transformer import Session
from billparser.db.models import ContentDiff, Section, Content
from billparser.logger import log
import re
from billparser.actions import ActionObject


name_extract = re.compile(r"\((?P<name>.+?)")


def redesignate(action_obj: ActionObject, session: "Session") -> None:
    """
    Handles changing the display letter to something new for a section

    Args:
        action_obj (ActionObject): Parsed action
        session (Session): Current database session
    """
    action = action_obj.action
    new_vers_id = action_obj.version_id
    cited_content = action_obj.cited_content
    from_name = name_extract.search(action.get("target", ""))
    to_name = name_extract.search(action.get("redesignation", ""))
    if from_name is None or to_name is None:
        return
    from_name = from_name.groupdict().get("name")
    to_name = to_name.groupdict().get("name")
    if from_name not in cited_content.section_display:
        log.warn("Not found?")
        return
    chapter = (
        session.query(Section)
        .filter(Section.section_id == cited_content.section_id)
        .limit(1)
        .all()
    )
    if len(chapter) > 0:
        chapter_id = chapter[0].chapter_id
        diff = ContentDiff(
            content_id=cited_content.content_id,
            section_id=cited_content.section_id,
            chapter_id=chapter_id,
            version_id=new_vers_id,
            section_display=cited_content.section_display.replace(from_name, to_name),
        )
        session.add(diff)
        session.commit()
