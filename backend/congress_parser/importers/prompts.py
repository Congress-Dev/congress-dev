from collections import defaultdict
import logging
from typing import Dict, List
from congress_parser.prompt_runners.bill_tagger import bill_tagger
from congress_parser.utils.logger import LogContext
from sqlalchemy import select, and_, not_
import litellm


from congress_db.models import PromptBatch, LegislationVersion, Prompt
from congress_db.session import Session

from congress_parser.prompt_runners.appropriation_finder import appropriation_finder
from congress_parser.prompt_runners.clause_tagger import clause_tagger
from congress_parser.prompt_runners.section_summarizer import section_summarizer


def get_outstanding_legis_versions(prompt_ids: List[int]) -> List[int]:
    """
    Get all legislation versions that have not been run for the given prompt ids
    """
    session = Session()

    query = (
        select([LegislationVersion.legislation_version_id])
        .outerjoin(
            PromptBatch,
            and_(
                LegislationVersion.legislation_version_id
                == PromptBatch.legislation_version_id,
                PromptBatch.prompt_id.in_(prompt_ids),
            ),
        )
        .where(PromptBatch.legislation_version_id == None)
    )

    # Execute the query
    results = session.execute(query).scalars().all()
    return results


if __name__ == "__main__":
    """
    Looks for bills without prompts run on them yet
    """
    session = Session()
    litellm._logging._disable_debugging()
    prompts = session.query(Prompt).all()

    prompts_by_name: Dict[str, Prompt] = defaultdict(list)

    for prompt in prompts:
        session.expunge(prompt)
        prompts_by_name[prompt.title].append(prompt)

    # Sort them by id for each prompt
    for prompt_name, prompt_list in prompts_by_name.items():
        prompt_list.sort(key=lambda x: x.prompt_id, reverse=True)

    for prompt_name, prompt_list in prompts_by_name.items():
        with LogContext(
            {"prompt": {"name": prompt_name, "prompt_id": prompt_list[0].prompt_id}}
        ):
            selected_prompt = prompt_list[0]
            prompt_id = selected_prompt.prompt_id
            # Reverse it so we do newer bills first
            results = get_outstanding_legis_versions([l.prompt_id for l in prompt_list])
            results.sort()
            results = results[::-1]
            logging.info(
                f"Found {len(results)} legislation versions without prompt batch for {prompt_name}"
            )
            if prompt_name == "Clause Tagger":

                # for legis_v_id in results:
                #     logging.info(f"Running clause tagger on {legis_v_id}")
                #     clause_tagger(legis_v_id, prompt_id)
                pass
            elif prompt_name == "Appropriation Finder":
                for legis_v_id in results:
                    logging.info(f"Running appropriation finder on {legis_v_id}")
                    appropriation_finder(legis_v_id, prompt_id)
            elif prompt_name == "Bill Summarizer":
                for legis_v_id in results:
                    logging.info(f"Running summarizer on {legis_v_id}")
                    section_summarizer(legis_v_id, prompt_id)
            elif prompt_name == "Bill Tagger":
                for legis_v_id in results:
                    logging.info(f"Running bill tagger on {legis_v_id}")
                    bill_tagger(legis_v_id, prompt_id)