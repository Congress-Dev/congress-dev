# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from congress_api.models.base_model_ import Model
from congress_api import util


class BillDiffMetadataItem(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, long_title=None, section_number=None, heading=None, display=None, short_title=None):  # noqa: E501
        """BillDiffMetadataItem - a model defined in OpenAPI

        :param long_title: The long_title of this BillDiffMetadataItem.  # noqa: E501
        :type long_title: str
        :param section_number: The section_number of this BillDiffMetadataItem.  # noqa: E501
        :type section_number: str
        :param heading: The heading of this BillDiffMetadataItem.  # noqa: E501
        :type heading: str
        :param display: The display of this BillDiffMetadataItem.  # noqa: E501
        :type display: str
        :param short_title: The short_title of this BillDiffMetadataItem.  # noqa: E501
        :type short_title: str
        """
        self.openapi_types = {
            'long_title': str,
            'section_number': str,
            'heading': str,
            'display': str,
            'short_title': str
        }

        self.attribute_map = {
            'long_title': 'long_title',
            'section_number': 'section_number',
            'heading': 'heading',
            'display': 'display',
            'short_title': 'short_title'
        }

        self._long_title = long_title
        self._section_number = section_number
        self._heading = heading
        self._display = display
        self._short_title = short_title

    @classmethod
    def from_dict(cls, dikt) -> 'BillDiffMetadataItem':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BillDiffMetadataItem of this BillDiffMetadataItem.  # noqa: E501
        :rtype: BillDiffMetadataItem
        """
        return util.deserialize_model(dikt, cls)

    @property
    def long_title(self):
        """Gets the long_title of this BillDiffMetadataItem.


        :return: The long_title of this BillDiffMetadataItem.
        :rtype: str
        """
        return self._long_title

    @long_title.setter
    def long_title(self, long_title):
        """Sets the long_title of this BillDiffMetadataItem.


        :param long_title: The long_title of this BillDiffMetadataItem.
        :type long_title: str
        """

        self._long_title = long_title

    @property
    def section_number(self):
        """Gets the section_number of this BillDiffMetadataItem.


        :return: The section_number of this BillDiffMetadataItem.
        :rtype: str
        """
        return self._section_number

    @section_number.setter
    def section_number(self, section_number):
        """Sets the section_number of this BillDiffMetadataItem.


        :param section_number: The section_number of this BillDiffMetadataItem.
        :type section_number: str
        """

        self._section_number = section_number

    @property
    def heading(self):
        """Gets the heading of this BillDiffMetadataItem.


        :return: The heading of this BillDiffMetadataItem.
        :rtype: str
        """
        return self._heading

    @heading.setter
    def heading(self, heading):
        """Sets the heading of this BillDiffMetadataItem.


        :param heading: The heading of this BillDiffMetadataItem.
        :type heading: str
        """

        self._heading = heading

    @property
    def display(self):
        """Gets the display of this BillDiffMetadataItem.


        :return: The display of this BillDiffMetadataItem.
        :rtype: str
        """
        return self._display

    @display.setter
    def display(self, display):
        """Sets the display of this BillDiffMetadataItem.


        :param display: The display of this BillDiffMetadataItem.
        :type display: str
        """

        self._display = display

    @property
    def short_title(self):
        """Gets the short_title of this BillDiffMetadataItem.


        :return: The short_title of this BillDiffMetadataItem.
        :rtype: str
        """
        return self._short_title

    @short_title.setter
    def short_title(self, short_title):
        """Sets the short_title of this BillDiffMetadataItem.


        :param short_title: The short_title of this BillDiffMetadataItem.
        :type short_title: str
        """

        self._short_title = short_title
