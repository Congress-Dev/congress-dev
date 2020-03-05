# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from congress_api import util
from congress_api.models.base_model_ import Model
from congress_api.models.bill_text_content import BillTextContent  # noqa: E501


class BillTextResponse(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(
        self,
        legislation_id=None,
        legislation_version_id=None,
        content=None,
        legislation_version=None,
    ):  # noqa: E501
        """BillTextResponse - a model defined in OpenAPI

        :param legislation_id: The legislation_id of this BillTextResponse.  # noqa: E501
        :type legislation_id: int
        :param legislation_version_id: The legislation_version_id of this BillTextResponse.  # noqa: E501
        :type legislation_version_id: int
        :param content: The content of this BillTextResponse.  # noqa: E501
        :type content: List[BillTextContent]
        :param legislation_version: The legislation_version of this BillTextResponse.  # noqa: E501
        :type legislation_version: str
        """
        self.openapi_types = {
            "legislation_id": int,
            "legislation_version_id": int,
            "content": List[BillTextContent],
            "legislation_version": str,
        }

        self.attribute_map = {
            "legislation_id": "legislation_id",
            "legislation_version_id": "legislation_version_id",
            "content": "content",
            "legislation_version": "legislation_version",
        }

        self._legislation_id = legislation_id
        self._legislation_version_id = legislation_version_id
        self._content = content
        self._legislation_version = legislation_version

    @classmethod
    def from_dict(cls, dikt) -> "BillTextResponse":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BillTextResponse of this BillTextResponse.  # noqa: E501
        :rtype: BillTextResponse
        """
        return util.deserialize_model(dikt, cls)

    @property
    def legislation_id(self):
        """Gets the legislation_id of this BillTextResponse.


        :return: The legislation_id of this BillTextResponse.
        :rtype: int
        """
        return self._legislation_id

    @legislation_id.setter
    def legislation_id(self, legislation_id):
        """Sets the legislation_id of this BillTextResponse.


        :param legislation_id: The legislation_id of this BillTextResponse.
        :type legislation_id: int
        """

        self._legislation_id = legislation_id

    @property
    def legislation_version_id(self):
        """Gets the legislation_version_id of this BillTextResponse.


        :return: The legislation_version_id of this BillTextResponse.
        :rtype: int
        """
        return self._legislation_version_id

    @legislation_version_id.setter
    def legislation_version_id(self, legislation_version_id):
        """Sets the legislation_version_id of this BillTextResponse.


        :param legislation_version_id: The legislation_version_id of this BillTextResponse.
        :type legislation_version_id: int
        """

        self._legislation_version_id = legislation_version_id

    @property
    def content(self):
        """Gets the content of this BillTextResponse.


        :return: The content of this BillTextResponse.
        :rtype: List[BillTextContent]
        """
        return self._content

    @content.setter
    def content(self, content):
        """Sets the content of this BillTextResponse.


        :param content: The content of this BillTextResponse.
        :type content: List[BillTextContent]
        """

        self._content = content

    @property
    def legislation_version(self):
        """Gets the legislation_version of this BillTextResponse.


        :return: The legislation_version of this BillTextResponse.
        :rtype: str
        """
        return self._legislation_version

    @legislation_version.setter
    def legislation_version(self, legislation_version):
        """Sets the legislation_version of this BillTextResponse.


        :param legislation_version: The legislation_version of this BillTextResponse.
        :type legislation_version: str
        """

        self._legislation_version = legislation_version