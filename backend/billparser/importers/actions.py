import os
import time
from typing import Dict, List
from billparser.db.models import LegislationActionParse, LegislationVersion
from joblib import Parallel, delayed
from sqlalchemy import func
from billparser.actions.parser import parse_bill_for_actions
from billparser.db.queries import get_legislation_versions, check_for_action_parses
from billparser.db.handler import Session, init_session

THREADS = int(os.environ.get("PARSE_THREADS", -4))


def get_legislation_versions() -> List[LegislationVersion]:
    """
    Returns a list of all legislation_version_ids
    """
    session = Session()
    results = session.query(LegislationVersion).all()
    session.expunge_all()
    return results


def check_for_action_parses(legislation_version_id: List[int]) -> Dict[int, int]:
    """
    Return a dict of the number of action parses for each legislation_version_id
    """
    session = Session()
    results = (
        session.query(
            LegislationActionParse.legislation_version_id,
            func.count(LegislationActionParse.legislation_action_parse_id),
        )
        .filter(
            LegislationActionParse.legislation_version_id.in_(legislation_version_id)
        )
        .group_by(LegislationActionParse.legislation_version_id)
        .all()
    )
    return {x[0]: x[1] for x in results}


if __name__ == "__main__":
    """
    Identify which bills need to have they actions parsed
    then parse them
    """
    all_legislation_versions = get_legislation_versions()
    action_parse_counts = check_for_action_parses(
        (x.legislation_version_id for x in all_legislation_versions)
    )
    valid_versions = []
    for legis_vers in all_legislation_versions:
        if legis_vers.legislation_version_id not in action_parse_counts:
            valid_versions.append(legis_vers)
        else:
            if action_parse_counts[legis_vers.legislation_version_id] == 0:
                valid_versions.append(legis_vers)
    print(f"Found {len(valid_versions)} versions to parse")
    session = Session()
    session.commit()
    time.sleep(5)
    Parallel(n_jobs=THREADS, verbose=5)(delayed(parse_bill_for_actions)(x) for x in valid_versions)
    # for version in valid_versions:
    #     try:
    #         parse_bill_for_actions(version)
    #     except:
    #         pass
