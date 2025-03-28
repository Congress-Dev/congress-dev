from congress_api.db.uscode_queries import (
    get_available_releases,
    get_available_titles,
    get_section_text,
    get_title_sections,
    get_section_levels,
    get_section_lineage
)
from congress_api.models.error_response import ErrorResponse  # noqa: E501
from congress_api.models.release_point_list import ReleasePointList  # noqa: E501
from congress_api.models.usc_section_content_list import (
    USCSectionContentList,
)  # noqa: E501
from congress_api.models.usc_section_list import USCSectionList  # noqa: E501
from congress_api.models.usc_title_list import USCTitleList  # noqa: E501


def get_usc_release_sections(release_vers, short_title) -> USCSectionList:  # noqa: E501
    """Your GET endpoint

    Get a list of the sections in this given title # noqa: E501

    :param release_vers:
    :type release_vers: str
    :param short_title:
    :type short_title: str
    :param page:
    :type page: int
    :param page_size:
    :type page_size: int

    :rtype: USCSectionList
    """
    try:
        resp = get_title_sections(release_vers, short_title)
        if resp is None:
            return ErrorResponse(message="No titles found for that release"), 404
        return resp
    except Exception as e:
        return ErrorResponse(message=str(e)), 500


def get_usc_release_text(
    release_vers, short_title, section_number
) -> USCSectionContentList:  # noqa: E501
    """Your GET endpoint

    Get the text for a specific section # noqa: E501

    :param release_vers:
    :type release_vers: str
    :param short_tile:
    :type short_tile: str
    :param section_number:
    :type section_number: str

    :rtype: USCSectionContentList
    """
    try:
        resp = get_section_text(release_vers, short_title, section_number)
        if resp is None:
            return ErrorResponse(message="No Content Found"), 200
        return resp
    except Exception as e:
        return ErrorResponse(message=str(e)), 500


def get_usc_release_titles(release_vers) -> USCTitleList:  # noqa: E501
    """Your GET endpoint

    Retrieve the list of titles loaded for a given release point. # noqa: E501

    :param release_vers: The given release point id, or latest
    :type release_vers: str

    :rtype: USCTitleList
    """
    try:
        resp = get_available_titles(release_vers)
        if resp is None:
            return ErrorResponse(message="No release found with that id"), 404
        return resp
    except Exception as e:
        return ErrorResponse(message=str(e)), 500


def get_usc_releases() -> ReleasePointList:  # noqa: E501
    """Your GET endpoint

    Retrieve the list of available release points # noqa: E501


    :rtype: ReleasePointList
    """
    try:
        return get_available_releases()
    except Exception as e:
        return ErrorResponse(message=str(e))

# TODO: It might make more sense to allow for passing the usc identifier
def get_usc_levels(release_vers, short_title, usc_section_id):  # noqa: E501
    """Your GET endpoint

    Gets the levels that are children of a given usc_section_id # noqa: E501

    :param release_vers: 
    :type release_vers: str
    :param short_title: 
    :type short_title: str
    :param usc_section_id: 
    :type usc_section_id: str

    :rtype: USCSectionList
    """
    try:
        resp = get_section_levels(release_vers, short_title, usc_section_id)
        if resp is None:
            return ErrorResponse(message="No levels found for this title and section"), 404
        return resp
    except Exception as e:
        return ErrorResponse(message=str(e)), 500

def get_usc_levels_base(release_vers, short_title):  # noqa: E501
    """Your GET endpoint

    Gets the levels that are children of a given usc_section_id # noqa: E501

    :param release_vers: 
    :type release_vers: str
    :param short_title: 
    :type short_title: str

    :rtype: USCSectionList
    """
    try:
        resp = get_section_levels(release_vers, short_title, None)
        if resp is None:
            return ErrorResponse(message="No levels found for this title and section"), 404
        return resp
    except Exception as e:
        return ErrorResponse(message=str(e)), 500

def get_usc_section_lineage(release_vers, short_title, usc_section_number):  # noqa: E501
    """get_section_lineage

    Returns the lineage of a particular usc_section_id # noqa: E501

    :param release_vers: 
    :type release_vers: str
    :param short_title: 
    :type short_title: str
    :param usc_section_number: 
    :type usc_section_number: str

    :rtype: USCSectionList
    """
    try:
        resp = get_section_lineage(release_vers, short_title, usc_section_number)
        if resp is None:
            return ErrorResponse(message="No lineage found for this title and section"), 404
        return resp
    except Exception as e:
        return ErrorResponse(message=str(e)), 500
