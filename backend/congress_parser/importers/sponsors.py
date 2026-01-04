from time import sleep

from congress_db.handler import Session, init_session
from congress_db.models import Legislation, LegislationSponsorship
from congress_parser.metadata.sponsors import extract_sponsors_from_api

MIN_TIME_BETWEEN_REQUESTS = 3600 / 5000

if __name__ == "__main__":
    init_session()

    session = Session()

    query = (
        session.query(Legislation)
        .outerjoin(
            LegislationSponsorship,
            Legislation.legislation_id == LegislationSponsorship.legislation_id,
        )
        .where(LegislationSponsorship.legislation_id == None)  # or LegislationSponsorship.legislation_id.is_(None)
        .order_by(Legislation.number)
    )

    results = query.all()
    result_count = len(results)
    for i in range(result_count):
        legislation = results[i]

        print(f"Extracting info for {legislation.chamber} - {legislation.number} - {legislation.title}")
        extract_sponsors_from_api(1, {
            'chamber': legislation.chamber,
            'bill_number': legislation.number
        }, legislation.legislation_id, session)

        if i < result_count - 1:
            sleep(MIN_TIME_BETWEEN_REQUESTS)