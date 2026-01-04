import os
from typing import List

from cachetools import TTLCache, cached
from flask_sqlalchemy_session import current_session

from congress_db.models import Congress
from congress_api.models.session_metadata import SessionMetadata  # noqa: E501

CACHE_TIME = int(os.environ.get("CACHE_TIME", 0))
CACHE_SIZE = int(os.environ.get("CACHE_SIZE", 512))


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_congress_sessions() -> List[SessionMetadata]:
    """
    Get a list of all of the Congress sessions
    Eventually we'll need to paginate this?

    Returns:
        List[SessionMetadata]: A list of the Congress session metadata
    """
    congresses: List[Congress] = current_session.query(Congress).all()
    results = [
        SessionMetadata(
            congress_id=congress.congress_id,
            session_number=congress.session_number,
            start_year=congress.start_year,
            end_year=congress.end_year,
        )
        for congress in congresses
    ]
    return results


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_congress(session_number: int) -> Congress:
    congress_result = (
        current_session.query(Congress)
        .filter(Congress.session_number == session_number)
        .all()
    )
    return congress_result


@cached(TTLCache(CACHE_SIZE, CACHE_TIME))
def get_congress_session(session_number: int) -> SessionMetadata:
    """
    Get the metadata on a specific session.


    Args:
        session_number (int): The session number to search on

    Returns:
        SessionMetadata: The metadata about the specific session
    """
    if not isinstance(session_number, int):
        raise TypeError
    congress_result = get_congress(session_number)

    if len(congress_result) > 0:
        congress = congress_result[0]
        return SessionMetadata(
            congress_id=congress.congress_id,
            session_number=congress.session_number,
            start_year=congress.start_year,
            end_year=congress.end_year,
        )
    return None
