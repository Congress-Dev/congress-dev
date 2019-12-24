from flask_sqlalchemy_session import current_session
from billparser.db.models import (
    Chapter,
    Section,
    Content,
    ContentDiff,
    Version,
    Bill,
    BillVersion,
    BillContent,
)
from billparser.db.caching import FromCache
from cachetools import cached, TTLCache
from sqlalchemy import or_, String
from sqlalchemy.sql.expression import cast
from sqlalchemy.sql import alias
import re

from typing import List

import platform

windows = platform.system() == "Windows"

DEFAULT_VERSION_ID = 1
CACHE_TIME = 600

if windows:
    CACHE_TIME = 0


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_chapters(version_id=DEFAULT_VERSION_ID) -> List[Chapter]:
    """
    Gets all the Chapters for the current version

    Returns:
        List[Chapter]: A list of all the
    """
    results = (
        current_session.query(Chapter)
        .filter(Chapter.version_id == DEFAULT_VERSION_ID)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bills(house: int, senate: int, query: str, incl: str, decl: str) -> List[Bill]:
    """
    Gets the Bill rows according to the filters.

    Args:
        house (int): Include House bills
        senate (int): Include Senate bills
        query (str): Text to search for in the title
        incl (str): Versions to include
        decl (str): Versions to exclude

    Returns:
        List[Bill]: Bill objects that pass the above filters
    """
    results = current_session.query(Bill).join(BillVersion)
    if house != 1:
        results = results.filter(Bill.chamber != "House")
    if senate != 1:
        results = results.filter(Bill.chamber != "Senate")
    if len(query) > 0:
        results = results.filter(
            or_(
                Bill.bill_title.ilike(f"%{query}%"),
                cast(Bill.bill_number, String).like(
                    re.sub(r"[^0-9\s]", "", query).strip()
                ),
            )
        )
    if incl != "":
        results = results.filter(BillVersion.bill_version.in_(incl.split(",")))
    if decl != "":
        results = results.filter(~BillVersion.bill_version.in_(decl.split(",")))
    results = (
        results.order_by(Bill.bill_number)
        .limit(100)
        .options(FromCache("default"))
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_versions() -> List[Version]:
    """
    Gets a list of all the Version rows that correspond to Bills

    Returns:
        List[Version]: List of Versions corresponding to the Bill versions
    """
    results = current_session.query(Version).filter(Version.base_id is not None).all()
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_revisions() -> List[Version]:
    """
    Gets a list of all the Version rows that correspond to USCode revisions

    Returns:
        List[Version]: List of Versions that are USCode revisions
    """
    results = current_session.query(Version).filter(Version.base_id is None).all()
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_latest_sections(chapter_number: str) -> List[Section]:
    """
    Gets the sections for the given Chapter, from the first USCode revision in the table

    Args:
        chapter_number (str): Given Chapter.number to look for

    Returns:
        List[Section]: List of Sections from the given Chapter
    """
    latest_base = (
        current_session.query(Version).filter(Version.base_id == None).all()[0]
    )
    chapter = (
        current_session.query(Chapter)
        .filter(Chapter.version_id == latest_base.version_id)
        .filter(Chapter.number == chapter_number)
        .first()
    )
    results = (
        current_session.query(Section)
        .filter(Section.chapter_id == chapter.chapter_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_sections(chapter_id: int, version_id: int) -> List[Section]:
    """
    Gets the sections from the chapter and version id

    Args:
        chapter_id (int): Chapter id to look at
        version_id (int): Version id to look at

    Returns:
        List[Section]: List of sections that match the criteria
    """
    results = (
        current_session.query(Section)
        .filter(Section.chapter_id == chapter_id, Section.version_id == version_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_latest_content(chapter_number: str, section_number: str) -> List[Content]:
    """
    Converts a chapter number and section number into chapter and version ids
    Then calls the get_content function with those arguments

    Args:
        chapter_number (str): The Chapter number to search for
        section_number (str): The Section number to search for

    Returns:
        List[Content]: List of Contents from the given section
    """
    latest_base = (
        current_session.query(Version).filter(Version.base_id == None).all()[0]
    )
    chapter = (
        current_session.query(Chapter)
        .filter(Chapter.version_id == latest_base.version_id)
        .filter(Chapter.number == chapter_number)
        .first()
    )
    section = (
        current_session.query(Section)
        .filter(Section.version_id == latest_base.version_id)
        .filter(Section.number == section_number)
        .filter(Section.chapter_id == chapter.chapter_id)
        .first()
    )
    return get_content(section.section_id, latest_base.version_id)


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_content(section_id: int, version_id: int) -> List[Content]:
    """
    Gets the contents of a given Section in a given Version

    TODO: Is version id redundent here?

    Args:
        section_id (int): Section id to look at
        version_id (int): Version id to look at

    Returns:
        List[Content]: Content that passes the above filter
    """
    results = (
        current_session.query(Content)
        .filter(Content.section_id == section_id, Content.version_id == version_id)
        .order_by(Content.order_number.asc())
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_content_versions(bill_version_id: int) -> List[Content]:
    """
    Returns the content versions for a given bill version id

    Args:
        bill_version_id (int): Given bill version id

    Returns:
        List[Content]: List of Content that corresponds to a given Bill
    """
    results = (
        current_session.query(Content)
        .filter(
            Version.bill_version_id == bill_version_id,
            Content.version_id == Version.version_id,
        )
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_diffs(bill_version_id: int) -> List[ContentDiff]:
    """
    Gets the ContentDiffs for a given bill_version_id

    Args:
        bill_version_id (int): Target bill version id

    Returns:
        List[ContentDiff]: List of ContentDiffs for the bill version
    """
    version = (
        current_session.query(Version)
        .filter(Version.bill_version_id == bill_version_id)
        .all()
    )
    if len(version) > 0:
        version = version[0]
    else:
        return []
    results = (
        current_session.query(ContentDiff)
        .filter(ContentDiff.version_id == version.version_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bill_contents(bill_version_id: int) -> List[BillContent]:
    """
    Returns the BillContent for a given bill_version

    Args:
        bill_version_id (int): BillVersion PK on the BillContent table

    Returns:
        List[BillContent]: Matching BillContent rows
    """
    results = (
        current_session.query(BillContent)
        .filter(BillContent.bill_version_id == bill_version_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bill_metadata(bill_version_id: int) -> dict:
    bill_version = (
        current_session.query(BillVersion)
        .filter(BillVersion.bill_version_id == bill_version_id)
        .all()
    )
    if len(bill_version) > 0:
        bill = (
            current_session.query(Bill)
            .filter(Bill.bill_id == bill_version[0].bill_id)
            .all()
        )
        if len(bill) > 0:
            return {
                "chamber": bill[0].chamber,
                "number": bill[0].bill_number,
                "version": bill_version[0].bill_version,
            }

    return {}


def get_revision_diff(base_id: int, new_id: int):
    # Gets the diffs between two versions
    # SELECT t1.section_id as old_s_id, t2.section_id as new_s_id, t1.usc_ident, t1.section_display as old_s_d, t2.section_display as new_s_d, t1.heading, t2.heading FROM sections as t1 JOIN sections as t2 ON t2.version_id = 2 WHERE t1.version_id = 1 AND t1.usc_ident = t2.usc_ident AND (t1.heading != t2.heading) LIMIT 5000;
    new_sections: Section = Section.alias("new")
    old_sections: Section = Section.alias("old")
    results = (
        current_session.query(new_sections.section_id, old_sections.section_id)
        .join(old_sections, old_sections.version_id == new_id)
        .filter(new_sections.version_id == base_id)
        .filter(old_sections.usc_ident == new_sections.usc_ident)
        .filter(old_sections.heading != new_sections.heading)
    ).all()
    return results
