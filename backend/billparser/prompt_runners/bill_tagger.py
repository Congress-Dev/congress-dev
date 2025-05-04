import logging
from typing import List
from billparser.db.models import (
    LegislationVersionTag,
    PromptBatch,
)
from billparser.db.handler import Session
import json
from billparser.utils.logger import LogContext
import jsonschema

from datetime import datetime
from billparser.prompt_runners.utils import (
    get_existing_batch_or_content,
    get_legis_by_parent_and_id,
    print_clause,
    run_query,
)

"""
class Categorization(TypedDict):
    tags: List[str]
"""
SCHEMA = {
    "type": "object",
    "properties": {
        "tags": {"type": "array", "items": {"type": "string"}},
    },
}


def normalize_tags(tags: List[str]) -> List[str]:
    # Convert everything to title case
    # Replace underscores with spaces
    # Remove any leading or trailing whitespace
    return list(
        set(
            [
                tag.replace("_", " ").replace(" and ", " & ").strip().title()
                for tag in tags
            ]
        )
    )


def bill_tagger(legis_version_id: int, prompt_id: int):
    with LogContext(
        {"legislation_version": {"legislation_version_id": legis_version_id}}
    ):
        session = Session()
        existing_prompt_batch, prompt, legis_content = get_existing_batch_or_content(
            legis_version_id, prompt_id, session
        )
        if existing_prompt_batch:
            return
        legis_by_parent, legis_by_id = get_legis_by_parent_and_id(legis_content)

        prompt_text = prompt.prompt
        prompt_batch = PromptBatch(
            prompt_id=prompt_id,
            legislation_version_id=legis_version_id,
            attempted=0,
            successful=0,
            failed=0,
            skipped=0,
            created_at=datetime.now(),
        )
        session.add(prompt_batch)
        session.commit()
        full_tags = set()
        legis_body = None
        for lc in legis_content:
            if lc.content_type == "legis-body":
                legis_body = lc
                break

        prompt_batch.attempted += 1
        try:
            clause = print_clause(
                legis_by_id, legis_by_parent, legis_body.legislation_content_id
            )
            query = prompt_text.format(clause=clause)
            response = run_query(
                query,
                prompt.model or "ollama/hf.co/bartowski/Qwen2.5-14B-Instruct-1M-GGUF:latest",
                num_ctx=100000,
            )
            resp_dict = json.loads(response.choices[0].message.content)
            jsonschema.validate(resp_dict, SCHEMA)
            tags = normalize_tags(resp_dict["tags"])
            full_tags.update(tags)
            tag_obj = LegislationVersionTag(
                prompt_batch_id=prompt_batch.prompt_batch_id,
                legislation_version_id=lc.legislation_version_id,
                tags=tags,
            )
            session.add(tag_obj)
            logging.debug(f"Tagged {lc.legislation_content_id} with {tags}")
            prompt_batch.successful += 1
        except Exception as e:
            prompt_batch.failed += 1
            logging.exception("Failed to tag clause")
            if full_tags is None:
                logging.warning("full_tags became None")
                full_tags = set()
            else:
                prompt_batch.skipped += 1
        prompt_batch.completed_at = datetime.now()
        # Store the prompt batch
        session.add(prompt_batch)
        session.commit()
