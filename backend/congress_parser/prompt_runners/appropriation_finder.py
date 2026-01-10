import logging
from typing import List
from congress_db.models import Appropriation
from congress_db.session import Session
import json
from congress_parser.utils.logger import LogContext
import jsonschema
from typing import List
from congress_db.models import Appropriation, PromptBatch
from congress_db.session import Session
from congress_parser.prompt_runners.utils import get_existing_batch_or_content, run_query
from datetime import datetime

SCHEMA = {
    "type": "object",
    "properties": {
        "amount": {"type": "number"},
        "brief_purpose": {"type": "string"},
        "expires_at": {"type": "string"},
        "fiscal_years": {"type": "array", "items": {"type": "integer"}},
        "related_bill": {"type": "string"},
        "sub_appropriations": {
            "type": "array",
            "items": {"$ref": "#/definitions/Appropriation"},
        },
    },
    "definitions": {"Appropriation": {"$ref": "#"}},
}


def convert_to_int(dollar_str: str) -> int:
    try:
        return int(float(str(dollar_str).replace("$", "").replace(",", "")))
    except:
        return 0


def appropriation_finder(
    legislation_version_id: int, prompt_id: int
) -> List[Appropriation]:
    with LogContext(
        {"legislation_version": {"legislation_version_id": legislation_version_id}}
    ):
        with Session() as session:
            existing_prompt_batch, prompt, legis_content = (
                get_existing_batch_or_content(
                    legislation_version_id, prompt_id, session
                )
            )
            if existing_prompt_batch:
                return
            prompt_text = prompt.prompt
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
            try_better_model = []
            for content in legis_content:
                with LogContext(
                    {
                        "legislation_content": {
                            "legislation_content_id": content.legislation_content_id
                        }
                    }
                ):
                    if content.content_str and "$" in content.content_str:
                        prompt_batch.attempted += 1
                        if len(content.content_str) > 2700:
                            # Too big for qwen
                            try_better_model.append(content)
                            continue
                    else:
                        prompt_batch.skipped += 1
                        if (prompt_batch.attempted + prompt_batch.skipped) % 10 == 0:
                            session.commit()
                        continue
                    query = prompt_text.format(clause=content.content_str)
                    try:
                        response = run_query(query, model=prompt.model or "ollama/qwen2.5:32b")
                        obj = json.loads(
                            response.json()["choices"][0]["message"]["content"]
                        )
                        jsonschema.validate(obj, SCHEMA)
                    except:
                        prompt_batch.failed += 1
                        continue

                    def recursive_load(a: dict, parent_id: int = None):
                        initial_amount = convert_to_int(a.get("initial_amount", 0) or 0)
                        new_amount = convert_to_int(a.get("new_amount", 0) or 0)
                        net_change = convert_to_int(a.get("net_change", 0) or 0)
                        new_spending = initial_amount == 0
                        if initial_amount == new_amount:
                            net_change = new_amount
                            new_spending = True
                        try:
                            approp = Appropriation(
                                amount=net_change,
                                fiscal_years=a.get("fiscal_years", []),
                                until_expended=a.get("until_expended", False),
                                new_spending=new_spending,
                                legislation_content_id=content.legislation_content_id,
                                legislation_version_id=legislation_version_id,
                                parent_id=parent_id,
                                prompt_batch_id=prompt_batch.prompt_batch_id,
                                purpose=a.get("brief_purpose", ""),
                            )
                            session.add(approp)
                        except:
                            logging.exception("Failed to parse appropriation")
                            prompt_batch.failed += 1
                        # Make sure to commit before we try to do the appropriation parent
                        if len(a.get("sub_appropriations", [])) > 0:
                            session.commit()
                        for children in a.get("sub_appropriations", []):
                            try:
                                recursive_load(children, approp.appropriation_id)
                            except:
                                pass

                    try:
                        if len(obj.get("appropriations", [])) > 0:
                            for approp in obj.get("appropriations", []):
                                recursive_load(approp, None)
                        else:
                            # Didn't find anything, put this into another list
                            try_better_model.append(content)
                        prompt_batch.successful += 1
                    except:
                        logging.exception("Failed to parse")
            if len(try_better_model) > 0:
                logging.info("Trying better model")
            # Do it separately so we don't move the model in and out of memory
            for content in try_better_model:
                with LogContext(
                    {
                        "legislation_content": {
                            "legislation_content_id": content.legislation_content_id
                        }
                    }
                ):
                    query = prompt_text.format(clause=content.content_str)
                    try:
                        response = run_query(query, model="ollama/nemotron:latest")
                        obj = json.loads(
                            response.json()["choices"][0]["message"]["content"]
                        )
                        jsonschema.validate(obj, SCHEMA)
                    except:
                        prompt_batch.failed += 1
                        continue

                    def recursive_load(a: dict, parent_id: int = None):
                        initial_amount = convert_to_int(a.get("initial_amount", 0) or 0)
                        new_amount = convert_to_int(a.get("new_amount", 0) or 0)
                        net_change = convert_to_int(a.get("net_change", 0) or 0)
                        new_spending = initial_amount == 0
                        if initial_amount == new_amount:
                            net_change = new_amount
                            new_spending = True
                        approp = Appropriation(
                            amount=net_change,
                            fiscal_years=a.get("fiscal_years", []),
                            until_expended=a.get("until_expended", False),
                            new_spending=new_spending,
                            legislation_content_id=content.legislation_content_id,
                            legislation_version_id=legislation_version_id,
                            parent_id=parent_id,
                            prompt_batch_id=prompt_batch.prompt_batch_id,
                            purpose=a.get("brief_purpose", ""),
                        )
                        session.add(approp)
                        # Make sure to commit before we try to do the appropriation parent
                        if len(a.get("sub_appropriations", [])) > 0:
                            session.commit()
                        for children in a.get("sub_appropriations", []):
                            try:
                                recursive_load(children, approp.appropriation_id)
                            except:
                                pass

                    try:
                        if len(obj.get("appropriations", [])) > 0:
                            for approp in obj.get("appropriations", []):
                                recursive_load(approp, None)
                    except:
                        logging.exception("Failed to parse with better model")
            prompt_batch.completed_at = datetime.now()
            try:
                session.commit()
            except:
                pass
