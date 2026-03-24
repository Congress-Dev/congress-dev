from typing import List, Optional, Tuple
from datetime import date

from sqlalchemy import select, func, desc, and_

from congress_db.models import (
    CRECIssue,
    CRECGranule,
    CRECSpeech,
    CRECBillReference,
    CRECSummary,
    Legislator,
)
from congress_fastapi.db.postgres import get_database
from congress_fastapi.models.congressional_record import (
    CRECIssueInfo,
    CRECGranuleInfo,
    CRECSpeechDetailInfo,
    CRECBillReferenceInfo,
    CRECSpeakerStatInfo,
    CRECActivityItem,
)


async def get_issues(
    start_date: Optional[date],
    end_date: Optional[date],
    chamber: Optional[str],
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[CRECIssueInfo], int]:
    database = await get_database()

    query = select(*CRECIssueInfo.sqlalchemy_columns()).select_from(CRECIssue)
    count_query = select(func.count(CRECIssue.crec_issue_id))

    if start_date:
        query = query.where(CRECIssue.issue_date >= start_date)
        count_query = count_query.where(CRECIssue.issue_date >= start_date)
    if end_date:
        query = query.where(CRECIssue.issue_date <= end_date)
        count_query = count_query.where(CRECIssue.issue_date <= end_date)

    total = await database.fetch_val(count_query)

    query = query.order_by(desc(CRECIssue.issue_date))
    query = query.limit(page_size).offset((page - 1) * page_size)

    results = await database.fetch_all(query)
    return [CRECIssueInfo(**r) for r in results], total


async def get_issue_detail(issue_id: int):
    database = await get_database()

    issue_query = select(*CRECIssueInfo.sqlalchemy_columns()).where(
        CRECIssue.crec_issue_id == issue_id
    )
    issue = await database.fetch_one(issue_query)
    if not issue:
        return None, []

    granules_query = (
        select(*CRECGranuleInfo.sqlalchemy_columns())
        .where(CRECGranule.crec_issue_id == issue_id)
        .order_by(CRECGranule.order_number)
    )
    granules = await database.fetch_all(granules_query)

    return CRECIssueInfo(**issue), [CRECGranuleInfo(**g) for g in granules]


async def get_granule_detail(granule_id: int):
    database = await get_database()

    granule_query = select(*CRECGranuleInfo.sqlalchemy_columns()).where(
        CRECGranule.crec_granule_id == granule_id
    )
    granule = await database.fetch_one(granule_query)
    if not granule:
        return None, [], None

    speeches_query = (
        select(
            CRECSpeech.crec_speech_id,
            CRECSpeech.speaker_raw,
            CRECSpeech.legislator_bioguide_id,
            CRECSpeech.order_number,
            CRECSpeech.content_text,
            CRECSpeech.word_count,
        )
        .where(CRECSpeech.crec_granule_id == granule_id)
        .order_by(CRECSpeech.order_number)
    )
    speech_rows = await database.fetch_all(speeches_query)

    speeches = []
    for row in speech_rows:
        refs_query = (
            select(
                CRECBillReference.crec_bill_reference_id,
                CRECBillReference.legislation_id,
                CRECBillReference.cite_text,
                CRECBillReference.cite_type,
                CRECBillReference.start_offset,
                CRECBillReference.end_offset,
            )
            .where(CRECBillReference.crec_speech_id == row["crec_speech_id"])
        )
        ref_rows = await database.fetch_all(refs_query)

        speech = CRECSpeechDetailInfo(
            crec_speech_id=row["crec_speech_id"],
            speaker_raw=row["speaker_raw"],
            legislator_bioguide_id=row["legislator_bioguide_id"],
            order_number=row["order_number"],
            content_text=row["content_text"],
            word_count=row["word_count"],
            bill_references=[CRECBillReferenceInfo(**r) for r in ref_rows],
        )
        speeches.append(speech)

    summary_query = (
        select(CRECSummary.summary)
        .where(
            CRECSummary.crec_granule_id == granule_id,
            CRECSummary.summary_type == "granule",
        )
        .limit(1)
    )
    summary_row = await database.fetch_one(summary_query)
    summary = summary_row["summary"] if summary_row else None

    return CRECGranuleInfo(**granule), speeches, summary


async def get_speaker_stats(
    start_date: Optional[date],
    end_date: Optional[date],
    chamber: Optional[str],
    limit: int = 20,
    page: int = 1,
) -> Tuple[List[CRECSpeakerStatInfo], int]:
    database = await get_database()

    conditions = [CRECSpeech.legislator_bioguide_id.isnot(None)]

    if start_date or end_date or chamber:
        join_conditions = []
        if start_date:
            join_conditions.append(CRECIssue.issue_date >= start_date)
        if end_date:
            join_conditions.append(CRECIssue.issue_date <= end_date)

        query = (
            select(
                CRECSpeech.legislator_bioguide_id.label("bioguide_id"),
                Legislator.first_name,
                Legislator.last_name,
                Legislator.party,
                Legislator.state,
                Legislator.image_url,
                func.sum(CRECSpeech.word_count).label("total_words"),
                func.count(CRECSpeech.crec_speech_id).label("speech_count"),
            )
            .join(CRECGranule, CRECSpeech.crec_granule_id == CRECGranule.crec_granule_id)
            .join(CRECIssue, CRECGranule.crec_issue_id == CRECIssue.crec_issue_id)
            .join(Legislator, CRECSpeech.legislator_bioguide_id == Legislator.bioguide_id)
            .where(and_(*conditions, *join_conditions))
        )

        if chamber:
            query = query.where(CRECGranule.section == chamber)
    else:
        query = (
            select(
                CRECSpeech.legislator_bioguide_id.label("bioguide_id"),
                Legislator.first_name,
                Legislator.last_name,
                Legislator.party,
                Legislator.state,
                Legislator.image_url,
                func.sum(CRECSpeech.word_count).label("total_words"),
                func.count(CRECSpeech.crec_speech_id).label("speech_count"),
            )
            .join(Legislator, CRECSpeech.legislator_bioguide_id == Legislator.bioguide_id)
            .where(and_(*conditions))
        )

    query = query.group_by(
        CRECSpeech.legislator_bioguide_id,
        Legislator.first_name,
        Legislator.last_name,
        Legislator.party,
        Legislator.state,
        Legislator.image_url,
    )

    count_subquery = query.subquery()
    total = await database.fetch_val(
        select(func.count()).select_from(count_subquery)
    )

    query = query.order_by(desc("total_words"))
    query = query.limit(limit).offset((page - 1) * limit)

    results = await database.fetch_all(query)
    return [CRECSpeakerStatInfo(**r) for r in results], total


async def get_activity_calendar(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> List[CRECActivityItem]:
    database = await get_database()

    query = (
        select(
            CRECIssue.issue_date.label("date"),
            func.count(CRECGranule.crec_granule_id).label("count"),
        )
        .join(CRECGranule, CRECIssue.crec_issue_id == CRECGranule.crec_issue_id)
        .group_by(CRECIssue.issue_date)
        .order_by(CRECIssue.issue_date)
    )

    if start_date:
        query = query.where(CRECIssue.issue_date >= start_date)
    if end_date:
        query = query.where(CRECIssue.issue_date <= end_date)

    results = await database.fetch_all(query)
    return [CRECActivityItem(**r) for r in results]
