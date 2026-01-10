from congress_db.session import Session
from congress_db.models import USCContentDiff, USCSection, USCContent
from congress_parser.logger import log
import re
from congress_parser.actions import ActionObject


name_extract = re.compile(r"\((?P<name>.+?)")

# TODO: Fix redesignation to fix usc_ident
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
    legislation_content = action_obj.legislation_content
    if legislation_content is not None:
        legislation_id = legislation_content.legislation_content_id
    else:
        legislation_id = None
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
        session.query(USCSection)
        .filter(USCSection.usc_section_id == cited_content.usc_section_id)
        .limit(1)
        .all()
    )
    if len(chapter) > 0:
        chapter_id = chapter[0].usc_chapter_id
        diff = USCContentDiff(
            usc_content_id=cited_content.usc_content_id,
            usc_section_id=cited_content.usc_section_id,
            usc_chapter_id=chapter_id,
            version_id=new_vers_id,
            section_display=cited_content.section_display.replace(from_name, to_name),
            legislation_content_id=legislation_id,
        )
        session.add(diff)
        session.commit()
