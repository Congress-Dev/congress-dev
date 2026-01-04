import json
from typing import List
from congress_parser.appropriations import calculate_appropriation
from congress_db.models import LegislationContent, Appropriation
from congress_db.handler import Session
from litellm import completion

query = """class Appropriation(TypedDict):
    amount: float
    brief_purpose: str
    expires_at: str
    fiscal_years: List[int]
    related_bill: str
    sub_appropriations: List[Appropriation]

Please respond in json.
Can you summarize the following clause, there may be multiple appropriations?
{clause}
"""

def llm_parse(legislation_version_id: int,
) -> List[Appropriation]:
    with Session() as session:
        contents = (
            session.query(LegislationContent)
            .filter(LegislationContent.legislation_version_id == legislation_version_id)
            .filter(LegislationContent.content_str.ilike("%$%"))
        )
        print("Found", contents.count(), "appropriations")
        
        for content in contents:
            response = completion(
                model="ollama/dolphin-mixtral:8x7b",
                messages=[
                    {
                        "role": "user",
                        "content": query.format(clause=content.content_str)
                    }
                ],
                api_base="http://10.0.0.120:11434",
                format = "json",
                timeout=60,
                max_tokens=10000
                )
            try:
                obj = json.loads(response.json()["choices"][0]["message"]["content"])
            except:
                print("Failed to load: ", response.json()["choices"][0]["message"]["content"])
                continue
            def convert_to_int(dollar_str: str) -> int:
                try:
                    return int(float(str(dollar_str).replace("$", "").replace(",", "")))
                except:
                    return 0
            def recursive_load(a: dict, parent_id: int = None):
                approp = Appropriation(
                    amount=convert_to_int(a["amount"]),
                    fiscal_years=a.get("fiscal_years", []),
                    until_expended=a.get("until_expended", False),
                    new_spending=True,
                    legislation_content_id=content.legislation_content_id,
                    legislation_version_id=legislation_version_id,
                    parent_id=parent_id,
                    purpose=a.get("brief_purpose", ""),
                )
                session.add(approp)
                session.commit()
                for children in a.get("sub_appropriations", []):
                    try:
                        recursive_load(children, approp.appropriation_id)
                    except:
                        pass
            try:
                recursive_load(obj, None)
            except:
                pass
            

async def parse_bill_for_appropriations(
    legislation_version_id: int,
) -> List[Appropriation]:
    with Session() as session:
        contents = (
            session.query(LegislationContent)
            .filter(LegislationContent.legislation_version_id == legislation_version_id)
            .filter(LegislationContent.content_str.ilike("%appropriated%"), LegislationContent.content_str.ilike("%$%"))
            .all()
        )
        appropriations = []
        print("Found", len(contents), "appropriations")
        for content in contents:
            try:
                res = calculate_appropriation(content)
                if res:
                    appropriations.append(res)
            except Exception as e:
                print(e)
                pass
        print("Created", len(appropriations), "appropriations")
        for appropriation in appropriations:
            session.add(
                Appropriation(
                    amount=appropriation.amount,
                    fiscal_years=appropriation.fiscal_years,
                    until_expended=appropriation.until_expended,
                    new_spending=appropriation.new_spending,
                    legislation_content_id=appropriation.legislation_content_id,
                    legislation_version_id=legislation_version_id,
                )
            )
        session.commit()
        session.flush()
    return appropriations
