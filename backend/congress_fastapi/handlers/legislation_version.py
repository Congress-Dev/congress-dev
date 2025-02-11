import json
import time
from typing import List

from billparser.prompt_runners.utils import run_query
from congress_fastapi.models.legislation.llm import LLMResponse
from sqlalchemy import select

from congress_fastapi.db.postgres import get_database
from billparser.db.models import (
    LegislationContentTag,
    LegislationContent,
    LegislationContentSummary,
)

from congress_fastapi.models.legislation import (
    LegislationClauseTag,
    LegislationClauseSummary,
)


async def get_legislation_version_tags_by_legislation_id(
    legislation_version_id: int,
) -> List[LegislationClauseTag]:
    database = await get_database()
    query = (
        select(
            *LegislationClauseTag.sqlalchemy_columns(),
        )
        .select_from(LegislationContent)
        .where(LegislationContent.legislation_version_id == legislation_version_id)
        .join(
            LegislationContentTag,
            LegislationContentTag.legislation_content_id
            == LegislationContent.legislation_content_id,
        )
        .order_by(LegislationContentTag.legislation_content_id)
    )
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


async def run_talk_to_bill_prompt(query: str, content: str) -> LLMResponse:
    prompt = """You are a helpful agent working on Congress.dev, you receive a query from the user and a piece of legislation content.
    You shall then answer their query using the legislation.
    If you do not know, under NO circumstances should you hallucinate or otherwise make stuff up.
    Please respond in raw Markdown format.
    ONLY PROVIDE RESPONSES RELATED TO THE LEGISLATION.
    EVERYTHING BELOW HERE IS USER INPUT
    ==== Query ====
    {query}
    
    ==== Legislation ====
    {content}""".format(
        query=query, content=content
    )
    start_time = time.time()
    response = run_query(prompt, model="ollama/hf.co/bartowski/Qwen2.5-14B-Instruct-1M-GGUF:latest", json=False)
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
