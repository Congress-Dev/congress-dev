from typing import List
from billparser.appropriations import calculate_appropriation
from billparser.db.models import LegislationContent, Appropriation
from billparser.db.handler import Session


async def parse_bill_for_appropriations(
    legislation_version_id: int,
) -> List[Appropriation]:
    with Session() as session:
        contents = (
            session.query(LegislationContent)
            .filter(LegislationContent.legislation_version_id == legislation_version_id)
        )
        appropriations = []
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
