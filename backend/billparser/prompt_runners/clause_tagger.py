from billparser.run_through import (
    parse_archive,
    ensure_congress,
    retrieve_existing_legislations,
)
from billparser.db.models import (
    Legislation,
    LegislationContent,
    LegislationVersion,
    LegislationVersionEnum,
    LegislationChamber,
    LegislationType,
    LegislationContentTag,
    USCContentDiff,
    USCContent,
    Version,
    USCSection,
    USCRelease,
    Congress,
    Base,
    Prompt,
    PromptBatch,
)
from billparser.db.handler import Session, engine
import json

from collections import defaultdict
from typing import Dict, Optional
from litellm import completion
import litellm
from datetime import datetime

litellm.turn_off_message_logging = True
litellm._logging._disable_debugging()


def run_query(query):
    response = completion(
        model="ollama/qwen2.5:32b",
        messages=[{"role": "user", "content": query}],
        api_base="http://10.0.0.120:11434",
        format="json",
        timeout=60,
        max_tokens=10000,
    )
    return response


def indent_block(block: str) -> str:
    """
    Indent the entire block of text
    """
    prefix = "\t"
    return "\n".join(f"{prefix}{line}" for line in block.splitlines())


def get_my_row_content(lc: LegislationContent) -> str:
    """
    Return a string that represents the lc's text
    take care not to print too many newlines or tabs
    """
    row = ""
    if lc.section_display:
        row += f"{lc.section_display} "
    if lc.heading:
        row += lc.heading + "\n"

    # Only tab if we have a content_str
    if lc.heading is not None and lc.heading.strip() and lc.content_str:
        row += "\t"
    if lc.content_str:
        row += lc.content_str + "\n"
    return row


def recurse(parents: Dict[int, LegislationContent], lc_id: int) -> str:
    printed_str = ""
    tab = "\t"
    newline_no_tab = "\n"
    for lc in parents[lc_id]:
        if lc.content_type != "quoted-block":
            printed_str += get_my_row_content(lc)
        else:
            printed_str += "```\n"
        res = recurse(parents, lc.legislation_content_id)
        if res.strip() != "":
            if lc.content_type == "quoted-block":
                printed_str += res
            else:
                printed_str += indent_block(res) + "\n"
        if lc.content_type == "quoted-block":
            printed_str += "\n```"
    return printed_str.strip()


def print_bill(legis_by_parent: Dict[Optional[int], LegislationContent]) -> str:
    # Find the Nones
    printed_str = ""
    for lc in legis_by_parent[None]:
        printed_str += recurse(legis_by_parent, lc.legislation_content_id)
    return printed_str


def print_clause(
    legis_by_id: Dict[int, LegislationContent],
    legis_by_parent: Dict[Optional[int], LegislationContent],
    lc_id: int,
) -> str:
    # Print the lc_id and all children
    printed_str = ""
    me = legis_by_id[lc_id]
    printed_str += get_my_row_content(me)
    printed_str += indent_block(recurse(legis_by_parent, lc_id))
    return printed_str


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
