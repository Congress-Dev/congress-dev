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

import platform

windows = platform.system() == "Windows"

DEFAULT_VERSION_ID = 1
CACHE_TIME = 600

if windows:
    CACHE_TIME = 0


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_chapters():
    results = (
        current_session.query(Chapter)
        .filter(Chapter.version_id == DEFAULT_VERSION_ID)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bills(house, senate, query, incl, decl):
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
def get_versions():
    results = current_session.query(Version).filter(Version.base_id is not None).all()
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_revisions():
    results = current_session.query(Version).filter(Version.base_id is None).all()
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_latest_sections(chapter_number):
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
def get_sections(chapter_id, version_id):
    results = (
        current_session.query(Section)
        .filter(Section.chapter_id == chapter_id, Section.version_id == version_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_latest_content(chapter_number, section_number):
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
def get_content(section_id, version_id):
    results = (
        current_session.query(Content)
        .filter(Content.section_id == section_id, Content.version_id == version_id)
        .order_by(Content.order_number.asc())
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_content_versions(version_id):
    print(version_id, isinstance(version_id, (int)))
    results = (
        current_session.query(Content)
        .filter(
            Version.bill_version_id == version_id,
            Content.version_id == Version.version_id,
        )
        .all()
    )
    print("Content versions", len(results))
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_diffs(bill_version_id):
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
    print("Diffs", len(results))
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bill_contents(bill_version_id):
    results = (
        current_session.query(BillContent)
        .filter(BillContent.bill_version_id == bill_version_id)
        .all()
    )
    return results


@cached(cache=TTLCache(maxsize=512, ttl=CACHE_TIME))
def get_bill_metadata(bill_version_id):
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
                "version": bill_version[0].bill_versiIon,
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
