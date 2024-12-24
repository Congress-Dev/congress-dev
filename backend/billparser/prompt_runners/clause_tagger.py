from billparser.db.models import (
    LegislationContent,
    LegislationContentTag,
    Prompt,
    PromptBatch,
)
from billparser.db.handler import Session
import json

from collections import defaultdict
from typing import List

from datetime import datetime
from billparser.prompt_runners.utils import print_clause, run_query


def clause_tagger(legis_version_id: int, prompt_id: int):
    session = Session()
    legis_content: List[LegislationContent] = (
        session.query(LegislationContent)
        .filter(LegislationContent.legislation_version_id == legis_version_id)
        .all()
    )
    prompt = session.query(Prompt).filter(Prompt.prompt_id == prompt_id).first()
    existing_prompt_batch = (
        session.query(PromptBatch)
        .filter(
            PromptBatch.prompt_id == prompt_id,
            PromptBatch.legislation_version_id == legis_version_id,
        )
        .first()
    )
    if existing_prompt_batch:
        print("Prompt batch already exists")
        return
    legis_by_parent = defaultdict(list)
    legis_by_id = {}
    for lc in legis_content:
        if lc is None:
            continue
        legis_by_parent[lc.parent_id].append(lc)
        legis_by_id[lc.legislation_content_id] = lc

    for keys, values in legis_by_parent.items():
        values.sort(key=lambda x: x.legislation_content_id)
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
    for lc in legis_content:
        if lc.content_str and "amended" in lc.content_str:
            prompt_batch.attempted += 1
            try:
                clause = print_clause(
                    legis_by_id, legis_by_parent, lc.legislation_content_id
                )
                query = prompt_text.format(clause=clause)
                response = run_query(query)
                resp_dict = json.loads(response.choices[0].message.content)
                tags = resp_dict["tags"]
                tag_obj = LegislationContentTag(
                    prompt_batch_id=prompt_batch.prompt_batch_id,
                    legislation_content_id=lc.legislation_content_id,
                    tags=tags,
                )
                tag_obj.validate()
                session.add(tag_obj)
                print(f"Tagged {lc.legislation_content_id} with {tags}")
                prompt_batch.successful += 1
            except Exception as e:
                prompt_batch.failed += 1
                print(e)
                continue
        else:
            prompt_batch.skipped += 1
    prompt_batch.completed_at = datetime.now()
    # Store the prompt batch
    session.add(prompt_batch)
    session.commit()
