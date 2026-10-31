from collections import defaultdict
import time
import logging
from typing import Dict, List, Optional, Tuple, Union
from congress_db.models import LegislationContent, Prompt, PromptBatch, USCContent
from litellm import completion
import litellm
import os

litellm.turn_off_message_logging = True
litellm._logging._disable_debugging()

# Model per use case, read from the environment. Intentionally no defaults:
# a use case without a configured model fails loudly instead of silently
# picking one.
MODEL_ENV_VARS = {
    "section_summary": "LLM_MODEL_SECTION_SUMMARY",
    "bill_tagger": "LLM_MODEL_BILL_TAGGER",
    "clause_tagger": "LLM_MODEL_CLAUSE_TAGGER",
    "appropriation_finder": "LLM_MODEL_APPROPRIATION_FINDER",
    "appropriation_finder_fallback": "LLM_MODEL_APPROPRIATION_FINDER_FALLBACK",
    "appropriations_parser": "LLM_MODEL_APPROPRIATIONS_PARSER",
    "talk_to_bill": "LLM_MODEL_TALK_TO_BILL",
}


def resolve_model(use_case: str, override: Optional[str] = None) -> str:
    """
    Return the OpenRouter model for ``use_case``: ``override`` (e.g. the
    ``prompts.prompt.model`` column) if set, else the use case's env var.
    """
    model = override or os.environ.get(MODEL_ENV_VARS[use_case], "")
    if not model.strip():
        raise ValueError(
            f"No LLM model configured for '{use_case}'. "
            f"Set {MODEL_ENV_VARS[use_case]} (e.g. 'vendor/model-name' from openrouter.ai/models)."
        )
    return model.strip()


def openrouter_model(model: str) -> str:
    if model.startswith("ollama/"):
        raise ValueError(
            f"Model '{model}' is an Ollama model, which is no longer supported. "
            "Use an OpenRouter model id (e.g. 'vendor/model-name')."
        )
    return model if model.startswith("openrouter/") else f"openrouter/{model}"


def run_query(
    query: str,
    model: str,
    *,
    json: bool = True,
    max_tokens: int = 10000,
) -> dict:
    """Run a single-turn prompt through OpenRouter (needs OPENROUTER_API_KEY)."""
    start_time = time.time()
    response = completion(
        model=openrouter_model(model),
        messages=[{"role": "user", "content": query}],
        response_format={"type": "json_object"} if json else None,
        timeout=120,
        max_tokens=max_tokens,
    )
    end_time = time.time()
    log_obj = {
        "response_time": end_time - start_time,
        "name": model,
    }
    if response.usage:
        if hasattr(response.usage, "prompt_tokens"):
            log_obj["input_tokens"] = response.usage.prompt_tokens
        if hasattr(response.usage, "completion_tokens"):
            log_obj["output_tokens"] = response.usage.completion_tokens
        if hasattr(response.usage, "total_tokens"):
            log_obj["total_tokens"] = response.usage.total_tokens
    logging.info(
        "Model response",
        extra={"model": log_obj},
    )
    return response


def indent_block(block: str) -> str:
    """
    Indent the entire block of text
    """
    prefix = "\t"
    return "\n".join(f"{prefix}{line}" for line in block.splitlines())


def get_my_row_content(lc: Union[LegislationContent, USCContent]) -> str:
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


def recurse(
    parents: Dict[int, Union[LegislationContent, USCContent]], lc_id: int
) -> str:
    printed_str = ""
    tab = "\t"
    newline_no_tab = "\n"
    for lc in parents[lc_id]:
        if lc.content_type != "quoted-block":
            printed_str += get_my_row_content(lc)
        else:
            printed_str += "```\n"
        res = recurse(
            parents,
            (
                lc.legislation_content_id
                if hasattr(lc, "legislation_content_id")
                else lc.usc_content_id
            ),
        )
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


def get_usc_content_by_parent_and_id(
    usc_content: List[USCContent],
) -> Tuple[Dict[int, List[USCContent]], Dict[int, USCContent]]:
    usc_by_parent = defaultdict(list)
    usc_by_id = {}
    for usc in usc_content:
        if usc is None:
            continue
        usc_by_parent[usc.parent_id].append(usc)
        usc_by_id[usc.usc_content_id] = usc
    for keys, values in usc_by_parent.items():
        values.sort(key=lambda x: x.usc_content_id)
    return usc_by_parent, usc_by_id
