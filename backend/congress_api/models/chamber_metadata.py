# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from congress_api import util
from congress_api.models.base_model_ import Model


class ChamberMetadata(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, bill_count=None, congress_id=None, chamber=None):  # noqa: E501
        """ChamberMetadata - a model defined in OpenAPI

        :param bill_count: The bill_count of this ChamberMetadata.  # noqa: E501
        :type bill_count: int
        :param congress_id: The congress_id of this ChamberMetadata.  # noqa: E501
        :type congress_id: int
        :param chamber: The chamber of this ChamberMetadata.  # noqa: E501
        :type chamber: str
        """
        self.openapi_types = {"bill_count": int, "congress_id": int, "chamber": str}

        self.attribute_map = {
            "bill_count": "bill_count",
            "congress_id": "congress_id",
            "chamber": "chamber",
        }

        self._bill_count = bill_count
        self._congress_id = congress_id
        self._chamber = chamber

    @classmethod
    def from_dict(cls, dikt) -> "ChamberMetadata":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ChamberMetadata of this ChamberMetadata.  # noqa: E501
        :rtype: ChamberMetadata
        """
        return util.deserialize_model(dikt, cls)

    @property
    def bill_count(self):
        """Gets the bill_count of this ChamberMetadata.


        :return: The bill_count of this ChamberMetadata.
        :rtype: int
        """
        return self._bill_count

    @bill_count.setter
    def bill_count(self, bill_count):
        """Sets the bill_count of this ChamberMetadata.


        :param bill_count: The bill_count of this ChamberMetadata.
        :type bill_count: int
        """

        self._bill_count = bill_count

    @property
    def congress_id(self):
        """Gets the congress_id of this ChamberMetadata.


        :return: The congress_id of this ChamberMetadata.
        :rtype: int
        """
        return self._congress_id

    @congress_id.setter
    def congress_id(self, congress_id):
        """Sets the congress_id of this ChamberMetadata.


        :param congress_id: The congress_id of this ChamberMetadata.
        :type congress_id: int
        """

        self._congress_id = congress_id

    @property
    def chamber(self):
        """Gets the chamber of this ChamberMetadata.


        :return: The chamber of this ChamberMetadata.
        :rtype: str
        """
        return self._chamber

    @chamber.setter
    def chamber(self, chamber):
        """Sets the chamber of this ChamberMetadata.


        :param chamber: The chamber of this ChamberMetadata.
        :type chamber: str
        """

        self._chamber = chamber
