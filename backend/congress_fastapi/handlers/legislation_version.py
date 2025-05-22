import json
import time
from typing import List
from collections import defaultdict

from billparser.prompt_runners.utils import run_query
from congress_fastapi.models.legislation.llm import LLMResponse
from sqlalchemy import select, text, and_, or_
from sqlalchemy.orm import Session, load_only

from congress_fastapi.db.postgres import get_database
from billparser.db.models import (
    LegislationContentTag,
    LegislationContent,
    LegislationContentSummary,
    Legislation,
    LegislationVersion,
    Congress,
    LegislationVersionTag as DBLegislationVersionTag,
    USCContentDiff,
    USCChapter,
    USCSection,
    USCContent,
)

from congress_fastapi.models.legislation import (
    LegislationClauseTag,
    LegislationClauseSummary,
    LegislationVersionMetadata,
    LegislationVersionTag,
)
from congress_fastapi.models.legislation.diff import BillDiffMetadataList, BillContentDiffMetadata


async def get_legislation_version_tags_by_legislation_id(
    legislation_version_id: int,
) -> List[LegislationVersionTag]:
    database = await get_database()
    query = select(
        *LegislationVersionTag.sqlalchemy_columns(),
    ).where(LegislationVersionTag.legislation_version_id == legislation_version_id)
    results = list(await database.fetch_all(query))
    if results is None or len(results) == 0:
        return None
    return [
        LegislationClauseTag.from_sqlalchemy(result) for result in results if result
    ]


async def get_legislation_version_summaries_by_legislation_id(
    legislation_version_id: int,
) -> List[LegislationClauseSummary]:
    database = await get_database()
    query = (
        select(
            *LegislationClauseSummary.sqlalchemy_columns(),
        )
        .select_from(LegislationContent)
        .where(LegislationContent.legislation_version_id == legislation_version_id)
        .join(
            LegislationContentSummary,
            LegislationContentSummary.legislation_content_id
            == LegislationContent.legislation_content_id,
        )
        .order_by(LegislationContentSummary.legislation_content_id)
    )
    results = list(await database.fetch_all(query))
    if results is None or len(results) == 0:
        return None
    return [
        LegislationClauseSummary.from_sqlalchemy(result) for result in results if result
    ]


async def get_legislation_version_summary_by_version(
    legislation_version_id: int,
) -> List[LegislationVersionMetadata]:
    database = await get_database()
    query = (
        select(
            *LegislationVersionMetadata.sqlalchemy_columns(),
        )
        .select_from(LegislationVersion)
        .where(LegislationVersion.legislation_version_id == legislation_version_id)
        .order_by(LegislationVersion.created_at.desc())
        .limit(1)
    )
    results = list(await database.fetch_all(query))
    if results is None or len(results) == 0:
        return None
    return [
        LegislationVersionMetadata.from_sqlalchemy(result)
        for result in results
        if result
    ]


async def run_talk_to_bill_prompt(
    query: str, content: str, metadata: str
) -> LLMResponse:
    prompt = """You are a helpful agent working on Congress.dev, you receive a query from the user and a piece of legislation content.
    You shall then answer their query using the legislation.
    If you do not know, under NO circumstances should you hallucinate or otherwise make stuff up.
    Please respond in raw Markdown format.
    ONLY PROVIDE RESPONSES RELATED TO THE LEGISLATION.
    EVERYTHING BELOW HERE IS USER INPUT
    ==== Query ====
    {query}
    ==== Metadata ====
    {metadata}
    ==== Legislation ====
    {content}""".format(
        query=query, content=content, metadata=metadata
    )
    start_time = time.time()
    response = run_query(
        prompt,
        model="ollama/hf.co/bartowski/Qwen2.5-14B-Instruct-1M-GGUF:latest",
        json=False,
        num_ctx=50000,
    )
    end_time = time.time()
    content = response.json()["choices"][0]["message"]["content"]
    if content.startswith("```markdown\n"):
        content = content[12:]
    if content.endswith("```"):
        content = content[:-3]
    return LLMResponse(
        response=content,
        tokens=(
            response.usage.total_tokens
            if response.usage and response.usage.total_tokens
            else 0
        ),
        time=end_time - start_time,
    )


async def get_legislation_version_diff_metadata_fastapi(
    legislation_version_id: int,
) -> List[BillDiffMetadataList]:
    database = await get_database()

    legis_version = await database.fetch_one(
        select(LegislationVersion).where(LegislationVersion.legislation_version_id == legislation_version_id)
    )

    if not legis_version:
        return []

    # Using a parameterized query for security
    query = (
        select(
            USCChapter.short_title,
            USCChapter.long_title,
            USCSection.number,
            USCSection.heading,
            USCSection.section_display,
            USCSection.usc_section_id,
        )
        .distinct()
        .select_from(USCContentDiff)
        .join(USCChapter, USCChapter.usc_chapter_id == USCContentDiff.usc_chapter_id)
        .join(USCSection, USCContentDiff.usc_section_id == USCSection.usc_section_id)
        .where(USCContentDiff.version_id == legis_version.version_id)
        .order_by(USCChapter.short_title, USCSection.number)
    )
    diff_sections = await database.fetch_all(query)
    
    # Get a list of all section_ids to query for repealed status
    section_ids = [row[5] for row in diff_sections]
    
    # Query to check for repealed sections
    repealed_sections = {}
    if section_ids:
        query_repealed = (
            select(
                USCContentDiff.usc_section_id,
            )
            .select_from(USCContentDiff)
            .where(
                and_(
                    USCContentDiff.version_id == legis_version.version_id,
                    USCContentDiff.usc_section_id.in_(section_ids),
                    or_(USCContentDiff.section_display.is_(None), USCContentDiff.section_display == '')
                )
            )
        )
        repealed_results = await database.fetch_all(query_repealed)
        
        # Create a dictionary of section_id -> repealed status
        for row in repealed_results:
            repealed_sections[row[0]] = True

    res_typed = defaultdict(lambda: {"long_title": None, "sections": []})
    for row in diff_sections:
        short_title = row[0]
        section_id = row[5]
        if res_typed[short_title]["long_title"] is None:
            res_typed[short_title]["long_title"] = row[1]
        
        # Check if this section is repealed
        is_repealed = repealed_sections.get(section_id, False)
        
        res_typed[short_title]["sections"].append(
            BillContentDiffMetadata(
                long_title=row[1],
                section_number=str(row[2]) if row[2] is not None else None,
                heading=row[3],
                display=row[4],
                repealed=is_repealed,
            )
        )

    output_list: List[BillDiffMetadataList] = []
    for short_title_key, data in res_typed.items():
        output_list.append(
            BillDiffMetadataList(
                legislation_version_id=legis_version.legislation_version_id,
                short_title=short_title_key,
                long_title=data["long_title"],
                sections=data["sections"],
            )
        )
        
    return sorted(output_list, key=lambda x: x.short_title)

