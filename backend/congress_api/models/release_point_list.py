# coding: utf-8

from __future__ import absolute_import

from datetime import date, datetime  # noqa: F401
from typing import Dict, List  # noqa: F401

from congress_api import util
from congress_api.models.base_model_ import Model
from congress_api.models.release_point_metadata import (
    ReleasePointMetadata,
)  # noqa: E501


class ReleasePointList(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, releases=None):  # noqa: E501
        """ReleasePointList - a model defined in OpenAPI

        :param releases: The releases of this ReleasePointList.  # noqa: E501
        :type releases: List[ReleasePointMetadata]
        """
        self.openapi_types = {"releases": List[ReleasePointMetadata]}

        self.attribute_map = {"releases": "releases"}

        self._releases = releases

    @classmethod
    def from_dict(cls, dikt) -> "ReleasePointList":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The ReleasePointList of this ReleasePointList.  # noqa: E501
        :rtype: ReleasePointList
        """
        return util.deserialize_model(dikt, cls)

    @property
    def releases(self):
        """Gets the releases of this ReleasePointList.


        :return: The releases of this ReleasePointList.
        :rtype: List[ReleasePointMetadata]
        """
        return self._releases

    @releases.setter
    def releases(self, releases):
        """Sets the releases of this ReleasePointList.


        :param releases: The releases of this ReleasePointList.
        :type releases: List[ReleasePointMetadata]
        """

        self._releases = releases
