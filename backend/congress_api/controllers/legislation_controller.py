from typing import List

from congress_api.db.chamber_queries import (
    get_chamber_bills_list,
    get_chamber_summary_obj,
    search_legislation,
)
from congress_api.db.legislation_queries import (
    get_legislation_details,
    get_legislation_version_details,
    get_legislation_version_text,
)
from congress_api.db.session_queries import get_congress_session, get_congress_sessions
from congress_api.models.bill_metadata import BillMetadata  # noqa: E501
from congress_api.models.bill_search_list import BillSearchList  # noqa: E501
from congress_api.models.bill_text_response import BillTextResponse  # noqa: E501
from congress_api.models.bill_version_metadata import BillVersionMetadata  # noqa: E501
from congress_api.models.chamber_bill_list import ChamberBillList  # noqa: E501
from congress_api.models.chamber_metadata import ChamberMetadata  # noqa: E501
from congress_api.models.error_response import ErrorResponse  # noqa: E501
from congress_api.models.session_metadata import SessionMetadata


def get_bill_summary(session, chamber, bill) -> BillMetadata:  # noqa: E501
    """get_bill_summary

    Get information about a specific bill # noqa: E501

    :param session: Congress session
    :type session: str
    :param chamber: The chamber of Congress to query
    :type chamber: str
    :param bill: The bill&#39;s number
    :type bill: str

    :rtype: BillMetadata
    """
    try:
        res = get_legislation_details(int(session), chamber, int(bill))
        if res is None:
            return ErrorResponse(message="No legislation found"), 404
        return res
    except Exception as e:
        return ErrorResponse(message=str(e)), 500
    return ErrorResponse(message="Hmm"), 404


def get_bill_version_amdts(
    session, chamber, bill, base_version, new_version
) -> ErrorResponse:  # noqa: E501
    """get_bill_version_amdts

    Gets the amendments made between the base version and the new version # noqa: E501

    :param session: Congress session
    :type session: str
    :param chamber: The chamber of Congress to query
    :type chamber: str
    :param bill: The bill&#39;s number
    :type bill: str
    :param base_version: The base version to compare against
    :type base_version: str
    :param new_version: The new version to compare with
    :type new_version: str

    :rtype: object
    """
    return ErrorResponse(message="Not Implemented"), 501


def get_bill_version_diffs(
    session, chamber, bill, version
) -> ErrorResponse:  # noqa: E501
    """get_bill_version_diffs

    Get information about a specific bill # noqa: E501

    :param session: Congress session
    :type session: str
    :param chamber: The chamber of Congress to query
    :type chamber: str
    :param bill: The bill&#39;s number
    :type bill: str
    :param version: The bill version to request
    :type version: str

    :rtype: object
    """
    return ErrorResponse(message="Not Implemented"), 501


def get_bill_version_summary(
    session, chamber, bill, version
) -> BillVersionMetadata:  # noqa: E501
    """get_bill_version_summary

    Get information about a specific bill version # noqa: E501

    :param session: Congress session
    :type session: str
    :param chamber: The chamber of Congress to query
    :type chamber: str
    :param bill: The bill&#39;s number
    :type bill: str
    :param version: The bill version to request
    :type version: str

    :rtype: BillVersionMetadata
    """
    try:
        res = get_legislation_version_details(int(session), chamber, int(bill), version)
        if res is None:
            return ErrorResponse(message="No legislation version found"), 404
        return res
    except Exception as e:
        return ErrorResponse(message=str(e)), 500
    return ErrorResponse(message="Hmm"), 404


def get_bill_version_text(
    session, chamber, bill, version, include_parsed=None
) -> BillTextResponse:  # noqa: E501
    """get_bill_version_text

    Get information about a specific bill # noqa: E501

    :param session: Congress session
    :type session: str
    :param chamber: The chamber of Congress to query
    :type chamber: str
    :param bill: The bill&#39;s number
    :type bill: str
    :param version: The bill version to request
    :type version: str
    :param include_parsed: Flag to include the parsed actions for each bit of text, defaults to false.
    :type include_parsed: bool

    :rtype: BillTextResponse
    """
    try:
        res = get_legislation_version_text(
            int(session), chamber, int(bill), version, include_parsed
        )
        if res is None:
            return ErrorResponse(message="No legislation version found"), 404
        return res
    except Exception as e:
        return ErrorResponse(message=str(e)), 500
    return ErrorResponse(message="Hmm"), 404


def get_chamber_bills(
    session, chamber, page_size=None, page=None
) -> ChamberBillList:  # noqa: E501
    """get_chamber_bills

    Retrieving a list of bills # noqa: E501

    :param session: Congress session
    :type session: str
    :param chamber: The chamber of Congress to query
    :type chamber: str
    :param page_size: Number of results
    :type page_size: int
    :param page: Pagination end, will default to 25 more than start
    :type page: str

    :rtype: ChamberBillList
    """
    try:
        res = get_chamber_bills_list(int(session), chamber, page_size, page)
        if res is None:
            return ErrorResponse(message="Bill not found"), 404
    except Exception as e:
        return ErrorResponse(message=e), 500
    return ErrorResponse(message="Not Found"), 404


def get_chamber_summary(session, chamber) -> ChamberMetadata:  # noqa: E501
    """Specific chamber

    Information about a specific chamber for the given session # noqa: E501

    :param session: Congress session
    :type session: str
    :param chamber: The chamber of Congress to query
    :type chamber: str

    :rtype: ChamberMetadata
    """
    try:
        chamber_summary = get_chamber_summary_obj(int(session), chamber)
        if chamber_summary is None:
            return ErrorResponse(message="Not found"), 404
        return chamber_summary
    except TypeError:
        return ErrorResponse(message="TypeError"), 500
    return ErrorResponse(message="Not found"), 404


def get_congress_search(
    congress=None, chamber=None, versions=None, text=None, page=None, page_size=None
) -> BillSearchList:  # noqa: E501
    """Your GET endpoint

    Search for the different bills # noqa: E501

    :param congress: Comma separated list of sessions to filter by
    :type congress: str
    :param chamber: Comma separated list of chambers to filter by
    :type chamber: str
    :param versions: Comma separated list of bill versions to include
    :type versions: str
    :param results: How many results to return
    :type results: int
    :param page: The page of results
    :type page:

    :rtype: BillSearchList
    """
    try:
        resp = search_legislation(congress, chamber, versions, text, page, page_size)
        return resp
    except Exception as e:
        return ErrorResponse(message=str(e)), 500
    return ErrorResponse(message="Not Implemented"), 501


def get_session_summary(session: str) -> SessionMetadata:  # noqa: E501
    """Specific Session

    Information about a specific session # noqa: E501

    :param session: Congress session
    :type session: str

    :rtype: SessionMetadata
    """
    try:
        specific_session = get_congress_session(int(session))
        if specific_session is None:
            return ErrorResponse(message=f'Session "{session}" not found')
        return specific_session

    except TypeError:
        return ErrorResponse(message="TypeError"), 404
    return ErrorResponse(message="Not found"), 404


def get_sessions_summary() -> List[SessionMetadata]:  # noqa: E501
    """Congress Sessions

    Returns a list of available congress sessions # noqa: E501


    :rtype: List[SessionMetadata]
    """
    all_sessions = get_congress_sessions()
    return all_sessions
