# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from congress_api import util
from congress_api.models.base_model_ import Model


class SessionMetadata(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(
        self, congress_id=None, session_number=None, start_year=None, end_year=None
    ):  # noqa: E501
        """SessionMetadata - a model defined in OpenAPI

        :param congress_id: The congress_id of this SessionMetadata.  # noqa: E501
        :type congress_id: int
        :param session_number: The session_number of this SessionMetadata.  # noqa: E501
        :type session_number: int
        :param start_year: The start_year of this SessionMetadata.  # noqa: E501
        :type start_year: int
        :param end_year: The end_year of this SessionMetadata.  # noqa: E501
        :type end_year: int
        """
        self.openapi_types = {
            "congress_id": int,
            "session_number": int,
            "start_year": int,
            "end_year": int,
        }

        self.attribute_map = {
            "congress_id": "congress_id",
            "session_number": "session_number",
            "start_year": "start_year",
            "end_year": "end_year",
        }

        self._congress_id = congress_id
        self._session_number = session_number
        self._start_year = start_year
        self._end_year = end_year

    @classmethod
    def from_dict(cls, dikt) -> "SessionMetadata":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The SessionMetadata of this SessionMetadata.  # noqa: E501
        :rtype: SessionMetadata
        """
        return util.deserialize_model(dikt, cls)

    @property
    def congress_id(self):
        """Gets the congress_id of this SessionMetadata.


        :return: The congress_id of this SessionMetadata.
        :rtype: int
        """
        return self._congress_id

    @congress_id.setter
    def congress_id(self, congress_id):
        """Sets the congress_id of this SessionMetadata.


        :param congress_id: The congress_id of this SessionMetadata.
        :type congress_id: int
        """

        self._congress_id = congress_id

    @property
    def session_number(self):
        """Gets the session_number of this SessionMetadata.


        :return: The session_number of this SessionMetadata.
        :rtype: int
        """
        return self._session_number

    @session_number.setter
    def session_number(self, session_number):
        """Sets the session_number of this SessionMetadata.


        :param session_number: The session_number of this SessionMetadata.
        :type session_number: int
        """

        self._session_number = session_number

    @property
    def start_year(self):
        """Gets the start_year of this SessionMetadata.


        :return: The start_year of this SessionMetadata.
        :rtype: int
        """
        return self._start_year

    @start_year.setter
    def start_year(self, start_year):
        """Sets the start_year of this SessionMetadata.


        :param start_year: The start_year of this SessionMetadata.
        :type start_year: int
        """

        self._start_year = start_year

    @property
    def end_year(self):
        """Gets the end_year of this SessionMetadata.


        :return: The end_year of this SessionMetadata.
        :rtype: int
        """
        return self._end_year

    @end_year.setter
    def end_year(self, end_year):
        """Sets the end_year of this SessionMetadata.


        :param end_year: The end_year of this SessionMetadata.
        :type end_year: int
        """

        self._end_year = end_year
