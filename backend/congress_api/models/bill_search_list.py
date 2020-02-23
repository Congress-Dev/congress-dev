# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from congress_api import util
from congress_api.models.base_model_ import Model
from congress_api.models.bill_metadata import BillMetadata  # noqa: E501
from congress_api.models.bill_search_list_params import (
    BillSearchListParams,
)  # noqa: E501


class BillSearchList(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, params=None, legislation=None):  # noqa: E501
        """BillSearchList - a model defined in OpenAPI

        :param params: The params of this BillSearchList.  # noqa: E501
        :type params: BillSearchListParams
        :param legislation: The legislation of this BillSearchList.  # noqa: E501
        :type legislation: List[BillMetadata]
        """
        self.openapi_types = {
            "params": BillSearchListParams,
            "legislation": List[BillMetadata],
        }

        self.attribute_map = {"params": "params", "legislation": "legislation"}

        self._params = params
        self._legislation = legislation

    @classmethod
    def from_dict(cls, dikt) -> "BillSearchList":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BillSearchList of this BillSearchList.  # noqa: E501
        :rtype: BillSearchList
        """
        return util.deserialize_model(dikt, cls)

    @property
    def params(self):
        """Gets the params of this BillSearchList.


        :return: The params of this BillSearchList.
        :rtype: BillSearchListParams
        """
        return self._params

    @params.setter
    def params(self, params):
        """Sets the params of this BillSearchList.


        :param params: The params of this BillSearchList.
        :type params: BillSearchListParams
        """

        self._params = params

    @property
    def legislation(self):
        """Gets the legislation of this BillSearchList.


        :return: The legislation of this BillSearchList.
        :rtype: List[BillMetadata]
        """
        return self._legislation

    @legislation.setter
    def legislation(self, legislation):
        """Sets the legislation of this BillSearchList.


        :param legislation: The legislation of this BillSearchList.
        :type legislation: List[BillMetadata]
        """

        self._legislation = legislation
