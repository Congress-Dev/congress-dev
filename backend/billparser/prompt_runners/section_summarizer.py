from typing import List, Optional
from billparser.db.models import LegislationContent, PromptBatch
from billparser.db.handler import Session
import json
import jsonschema
from typing import List
from billparser.db.models import LegislationContentSummary
from billparser.db.handler import Session
from billparser.prompt_runners.utils import (
    get_existing_batch_or_content,
    get_legis_by_parent_and_id,
    print_clause,
    run_query,
)
from datetime import datetime

"""class Summary(TypedDict):
    summary: str
"""
SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
    },
}


def section_summarizer(
    legislation_version_id: int, prompt_id: int
) -> List[LegislationContentSummary]:
    with Session() as session:
        existing_prompt_batch, prompt, legis_content = get_existing_batch_or_content(
            legislation_version_id, prompt_id, session
        )
        if existing_prompt_batch:
            return
        # Split them apart then strip them
        section_prompt, summary_prompt = prompt.prompt.split("=====", 1)
        section_prompt = section_prompt.strip()
        summary_prompt = summary_prompt.strip()

        prompt_batch = PromptBatch(
            prompt_id=prompt_id,
            legislation_version_id=legislation_version_id,
            attempted=0,
            successful=0,
            failed=0,
            skipped=0,
            created_at=datetime.now(),
        )
        session.add(prompt_batch)
        session.commit()

        legis_by_parent, legis_by_id = get_legis_by_parent_and_id(legis_content)

        def inside_quote_block(legis_id: int) -> bool:
            if legis_id is None:
                return False
            if legis_by_id[legis_id].content_type == "quoted-block":
                return True
            return inside_quote_block(legis_by_id[legis_id].parent_id)

        legis_body: Optional[LegislationContent] = None
        summaries = []
        for lc in legis_content:
            if lc.content_type == "legis-body":
                legis_body = lc
                continue
            elif lc.content_type == "section" and not inside_quote_block(
                lc.legislation_content_id
            ):
                # TODO: Verify we are not in a quote block
                print(f"Attempting to summarize: {lc.legislation_content_id}")
                prompt_batch.attempted += 1
                section_text = print_clause(
                    legis_by_id, legis_by_parent, lc.legislation_content_id
                )
                query = section_prompt.format(section=section_text)
                try:
                    response = run_query(query, model="ollama/gemma2:27b")
                    obj = json.loads(
                        response.json()["choices"][0]["message"]["content"]
                    )
                    jsonschema.validate(obj, SCHEMA)
                    summary = obj["summary"]
                    summary_lc = LegislationContentSummary(
                        legislation_content_id=lc.legislation_content_id,
                        prompt_batch_id=prompt_batch.prompt_batch_id,
                        summary=summary,
                    )
                    session.add(summary_lc)
                    prompt_batch.successful += 1
                    summaries.append(summary)
                except Exception as e:
                    print(e)
                    prompt_batch.failed += 1
            else:
                prompt_batch.skipped += 1
        # Summarize all of them now
        print(f"Summarizing all sections for {legislation_version_id}")
        try:
            query = summary_prompt.format(summaries="\n".join(x for x in summaries))
            resp = run_query(query, model="ollama/gemma2:27b")
            result = json.loads(resp.choices[0].message.content)
            jsonschema.validate(result, SCHEMA)
            summary_lc = LegislationContentSummary(
                legislation_content_id=legis_body.legislation_content_id,
                prompt_batch_id=prompt_batch.prompt_batch_id,
                summary=result["summary"],
            )
            session.add(summary_lc)
            prompt_batch.successful += 1
        except:
            prompt_batch.failed += 1
        prompt_batch.completed_at = datetime.now()
        session.commit()
