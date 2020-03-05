# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from congress_api import util
from congress_api.models.base_model_ import Model


class BillVersionMetadata(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(
        self,
        legislation_id=None,
        legislation_version_id=None,
        effective_date=None,
        created_at=None,
        legislation_version=None,
    ):  # noqa: E501
        """BillVersionMetadata - a model defined in OpenAPI

        :param legislation_id: The legislation_id of this BillVersionMetadata.  # noqa: E501
        :type legislation_id: int
        :param legislation_version_id: The legislation_version_id of this BillVersionMetadata.  # noqa: E501
        :type legislation_version_id: int
        :param effective_date: The effective_date of this BillVersionMetadata.  # noqa: E501
        :type effective_date: str
        :param created_at: The created_at of this BillVersionMetadata.  # noqa: E501
        :type created_at: str
        :param legislation_version: The legislation_version of this BillVersionMetadata.  # noqa: E501
        :type legislation_version: str
        """
        self.openapi_types = {
            "legislation_id": int,
            "legislation_version_id": int,
            "effective_date": str,
            "created_at": str,
            "legislation_version": str,
        }

        self.attribute_map = {
            "legislation_id": "legislation_id",
            "legislation_version_id": "legislation_version_id",
            "effective_date": "effective_date",
            "created_at": "created_at",
            "legislation_version": "legislation_version",
        }

        self._legislation_id = legislation_id
        self._legislation_version_id = legislation_version_id
        self._effective_date = effective_date
        self._created_at = created_at
        self._legislation_version = legislation_version

    @classmethod
    def from_dict(cls, dikt) -> "BillVersionMetadata":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BillVersionMetadata of this BillVersionMetadata.  # noqa: E501
        :rtype: BillVersionMetadata
        """
        return util.deserialize_model(dikt, cls)

    @property
    def legislation_id(self):
        """Gets the legislation_id of this BillVersionMetadata.

        Primary Key in the legislation table  # noqa: E501

        :return: The legislation_id of this BillVersionMetadata.
        :rtype: int
        """
        return self._legislation_id

    @legislation_id.setter
    def legislation_id(self, legislation_id):
        """Sets the legislation_id of this BillVersionMetadata.

        Primary Key in the legislation table  # noqa: E501

        :param legislation_id: The legislation_id of this BillVersionMetadata.
        :type legislation_id: int
        """

        self._legislation_id = legislation_id

    @property
    def legislation_version_id(self):
        """Gets the legislation_version_id of this BillVersionMetadata.


        :return: The legislation_version_id of this BillVersionMetadata.
        :rtype: int
        """
        return self._legislation_version_id

    @legislation_version_id.setter
    def legislation_version_id(self, legislation_version_id):
        """Sets the legislation_version_id of this BillVersionMetadata.


        :param legislation_version_id: The legislation_version_id of this BillVersionMetadata.
        :type legislation_version_id: int
        """

        self._legislation_version_id = legislation_version_id

    @property
    def effective_date(self):
        """Gets the effective_date of this BillVersionMetadata.


        :return: The effective_date of this BillVersionMetadata.
        :rtype: str
        """
        return self._effective_date

    @effective_date.setter
    def effective_date(self, effective_date):
        """Sets the effective_date of this BillVersionMetadata.


        :param effective_date: The effective_date of this BillVersionMetadata.
        :type effective_date: str
        """

        self._effective_date = effective_date

    @property
    def created_at(self):
        """Gets the created_at of this BillVersionMetadata.


        :return: The created_at of this BillVersionMetadata.
        :rtype: str
        """
        return self._created_at

    @created_at.setter
    def created_at(self, created_at):
        """Sets the created_at of this BillVersionMetadata.


        :param created_at: The created_at of this BillVersionMetadata.
        :type created_at: str
        """

        self._created_at = created_at

    @property
    def legislation_version(self):
        """Gets the legislation_version of this BillVersionMetadata.


        :return: The legislation_version of this BillVersionMetadata.
        :rtype: str
        """
        return self._legislation_version

    @legislation_version.setter
    def legislation_version(self, legislation_version):
        """Sets the legislation_version of this BillVersionMetadata.


        :param legislation_version: The legislation_version of this BillVersionMetadata.
        :type legislation_version: str
        """

        self._legislation_version = legislation_version