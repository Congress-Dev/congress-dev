import os
from typing import List, Optional
import chromadb
from chromadb.api.models.AsyncCollection import AsyncCollection
from chromadb.api.types import IncludeEnum
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from sqlalchemy import select, or_

from congress_fastapi.db.postgres import get_database
from congress_db.models import (
    USCContent,
    USCChapter,
    USCSection,
)

chroma_host = (
    os.environ.get(
        "CHROMA_HOST",
        os.environ.get("LLM_HOST", "10.0.0.120"),
    )
    .split("http://")[-1]
    .split(":")[0]
)


async def get_usc_content_by_citation(citation: str) -> Optional[USCContent]:
    database = await get_database()
    query = select(USCContent).where(USCContent.usc_ident == citation)
    result = await database.fetch_one(query)
    return result


async def get_usc_content_by_citations(citations: List[str]) -> List[USCContent]:
    database = await get_database()
    query = select(
        USCContent,
    ).where(
        or_(*[USCContent.usc_ident == cite for cite in citations]),
        USCContent.version_id == 74573,
    )
    results = await database.fetch_all(query)
    return results


async def get_usc_chapter_by_short_title(short_title: str) -> Optional[USCChapter]:
    database = await get_database()
    query = select(USCChapter).where(USCChapter.short_title == short_title)
    result = await database.fetch_one(query)
    return result


async def get_usc_chapter_by_short_titles(short_titles: List[str]) -> List[USCChapter]:
    r = []
    for title in short_titles:
        if len(title) < 2:
            title = "0" + title
        r.append(title)
    short_titles = r
    database = await get_database()
    query = select(
        USCChapter,
    ).where(
        or_(*[USCChapter.short_title == title for title in short_titles]),
        USCChapter.version_id == 74573,
    )
    results = await database.fetch_all(query)
    return results


async def read_usc_content(congress_id: int, citation: str) -> List[USCContent]:
    database = await get_database()
    query = (
        select(USCContent)
        .join(USCChapter, USCChapter.usc_release_id == congress_id)
        .join(USCSection, USCSection.usc_chapter_id == USCChapter.usc_chapter_id)
        .where(
            USCContent.usc_section_id == USCSection.usc_section_id,
                USCContent.usc_ident.ilike(citation),
        )
    )
    return await database.fetch_all(query)


async def search_chroma(query: str, num: int) -> List[dict]:
    CHROMADB = await chromadb.AsyncHttpClient(
        host=chroma_host,
        port=8000,
        ssl=False,
        headers=None,
        settings=Settings(),
        tenant="congress-dev",
        database="usc-chat",
    )
    collection: AsyncCollection = await CHROMADB.get_collection("uscode")
    response = await collection.query(
        query_texts=[query], n_results=num, include=[IncludeEnum.metadatas]
    )
    usc_contents = await get_usc_content_by_citations(response["ids"][0])
    short_titles = [x.usc_ident.split("/")[3].split("t")[-1] for x in usc_contents]
    usc_chapters = await get_usc_chapter_by_short_titles(short_titles)
    chapters_by_id = {f"t{x.short_title.strip()}": x for x in usc_chapters}

    contents_by_id = {x.usc_ident: x for x in usc_contents}

    results_by_id = {}
    for ident, content in contents_by_id.items():
        result = {}
        short_title = ident.split("/")[3]
        chapter = chapters_by_id.get(short_title.lower().strip())
        if chapter:
            result["title"] = chapter.long_title.capitalize().strip()
        else:
            result["title"] = short_title.capitalize()
        result["section_display"] = content.heading.strip()
        result["usc_link"] = f"{short_title[1:]}/{content.number}"
        result["usc_ident"] = ident
        results_by_id[ident] = result
    return [results_by_id[ident] for ident in response["ids"][0] if ident in results_by_id]
