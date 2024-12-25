from collections import defaultdict
from typing import Dict, List, Optional, Tuple
from billparser.db.models import LegislationContent, Prompt, PromptBatch
from litellm import completion
import litellm

litellm.turn_off_message_logging = True
litellm._logging._disable_debugging()


def run_query(query: str, model: str = "ollama/qwen2.5:32b") -> dict:
    response = completion(
        model=model,
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


def get_existing_batch_or_content(
    legislation_version_id: int, prompt_id: int, session
) -> Tuple[bool, Prompt, List[LegislationContent]]:
    """
    Retrieves the prompt, checks if there is an existing prompt batch, and retrieves the legislation content
    """
    prompt = session.query(Prompt).filter(Prompt.prompt_id == prompt_id).first()
    existing_prompt_batch = (
        session.query(PromptBatch)
        .filter(
            PromptBatch.prompt_id == prompt_id,
            PromptBatch.legislation_version_id == legislation_version_id,
        )
        .first()
    )
    if existing_prompt_batch:
        print("Prompt batch already exists")
        return True, prompt, []

    # Don't pull the content till we know we are gonna use it
    legis_content: List[LegislationContent] = (
        session.query(LegislationContent)
        .filter(LegislationContent.legislation_version_id == legislation_version_id)
        .all()
    )
    return False, prompt, legis_content


def get_legis_by_parent_and_id(
    legis_content: List[LegislationContent],
) -> Tuple[Dict[int, List[LegislationContent]], Dict[int, LegislationContent]]:
    legis_by_parent = defaultdict(list)
    legis_by_id = {}
    for lc in legis_content:
        if lc is None:
            continue
        legis_by_parent[lc.parent_id].append(lc)
        legis_by_id[lc.legislation_content_id] = lc
    for keys, values in legis_by_parent.items():
        values.sort(key=lambda x: x.legislation_content_id)
    return legis_by_parent, legis_by_id
