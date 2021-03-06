# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from congress_api.models.base_model_ import Model
from congress_api import util


class BillTextContent(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(
        self,
        legislation_content_id=None,
        parent_id=None,
        order_number=None,
        section_display=None,
        heading=None,
        content_str=None,
        content_type=None,
        action=None,
        lc_ident=None,
    ):  # noqa: E501
        """BillTextContent - a model defined in OpenAPI

        :param legislation_content_id: The legislation_content_id of this BillTextContent.  # noqa: E501
        :type legislation_content_id: int
        :param parent_id: The parent_id of this BillTextContent.  # noqa: E501
        :type parent_id: int
        :param order_number: The order_number of this BillTextContent.  # noqa: E501
        :type order_number: int
        :param section_display: The section_display of this BillTextContent.  # noqa: E501
        :type section_display: str
        :param heading: The heading of this BillTextContent.  # noqa: E501
        :type heading: str
        :param content_str: The content_str of this BillTextContent.  # noqa: E501
        :type content_str: str
        :param content_type: The content_type of this BillTextContent.  # noqa: E501
        :type content_type: str
        :param action: The action of this BillTextContent.  # noqa: E501
        :type action: object
        :param lc_ident: The lc_ident of this BillTextContent.  # noqa: E501
        :type lc_ident: str
        """
        self.openapi_types = {
            "legislation_content_id": int,
            "parent_id": int,
            "order_number": int,
            "section_display": str,
            "heading": str,
            "content_str": str,
            "content_type": str,
            "action": object,
            "lc_ident": str,
        }

        self.attribute_map = {
            "legislation_content_id": "legislation_content_id",
            "parent_id": "parent_id",
            "order_number": "order_number",
            "section_display": "section_display",
            "heading": "heading",
            "content_str": "content_str",
            "content_type": "content_type",
            "action": "action",
            "lc_ident": "lc_ident",
        }

        self._legislation_content_id = legislation_content_id
        self._parent_id = parent_id
        self._order_number = order_number
        self._section_display = section_display
        self._heading = heading
        self._content_str = content_str
        self._content_type = content_type
        self._action = action
        self._lc_ident = lc_ident

    @classmethod
    def from_dict(cls, dikt) -> "BillTextContent":
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The BillTextContent of this BillTextContent.  # noqa: E501
        :rtype: BillTextContent
        """
        return util.deserialize_model(dikt, cls)

    @property
    def legislation_content_id(self):
        """Gets the legislation_content_id of this BillTextContent.


        :return: The legislation_content_id of this BillTextContent.
        :rtype: int
        """
        return self._legislation_content_id

    @legislation_content_id.setter
    def legislation_content_id(self, legislation_content_id):
        """Sets the legislation_content_id of this BillTextContent.


        :param legislation_content_id: The legislation_content_id of this BillTextContent.
        :type legislation_content_id: int
        """

        self._legislation_content_id = legislation_content_id

    @property
    def parent_id(self):
        """Gets the parent_id of this BillTextContent.


        :return: The parent_id of this BillTextContent.
        :rtype: int
        """
        return self._parent_id

    @parent_id.setter
    def parent_id(self, parent_id):
        """Sets the parent_id of this BillTextContent.


        :param parent_id: The parent_id of this BillTextContent.
        :type parent_id: int
        """

        self._parent_id = parent_id

    @property
    def order_number(self):
        """Gets the order_number of this BillTextContent.


        :return: The order_number of this BillTextContent.
        :rtype: int
        """
        return self._order_number

    @order_number.setter
    def order_number(self, order_number):
        """Sets the order_number of this BillTextContent.


        :param order_number: The order_number of this BillTextContent.
        :type order_number: int
        """

        self._order_number = order_number

    @property
    def section_display(self):
        """Gets the section_display of this BillTextContent.


        :return: The section_display of this BillTextContent.
        :rtype: str
        """
        return self._section_display

    @section_display.setter
    def section_display(self, section_display):
        """Sets the section_display of this BillTextContent.


        :param section_display: The section_display of this BillTextContent.
        :type section_display: str
        """

        self._section_display = section_display

    @property
    def heading(self):
        """Gets the heading of this BillTextContent.


        :return: The heading of this BillTextContent.
        :rtype: str
        """
        return self._heading

    @heading.setter
    def heading(self, heading):
        """Sets the heading of this BillTextContent.


        :param heading: The heading of this BillTextContent.
        :type heading: str
        """

        self._heading = heading

    @property
    def content_str(self):
        """Gets the content_str of this BillTextContent.


        :return: The content_str of this BillTextContent.
        :rtype: str
        """
        return self._content_str

    @content_str.setter
    def content_str(self, content_str):
        """Sets the content_str of this BillTextContent.


        :param content_str: The content_str of this BillTextContent.
        :type content_str: str
        """

        self._content_str = content_str

    @property
    def content_type(self):
        """Gets the content_type of this BillTextContent.


        :return: The content_type of this BillTextContent.
        :rtype: str
        """
        return self._content_type

    @content_type.setter
    def content_type(self, content_type):
        """Sets the content_type of this BillTextContent.


        :param content_type: The content_type of this BillTextContent.
        :type content_type: str
        """

        self._content_type = content_type

    @property
    def action(self):
        """Gets the action of this BillTextContent.


        :return: The action of this BillTextContent.
        :rtype: object
        """
        return self._action

    @action.setter
    def action(self, action):
        """Sets the action of this BillTextContent.


        :param action: The action of this BillTextContent.
        :type action: object
        """

        self._action = action

    @property
    def lc_ident(self):
        """Gets the lc_ident of this BillTextContent.


        :return: The lc_ident of this BillTextContent.
        :rtype: str
        """
        return self._lc_ident

    @lc_ident.setter
    def lc_ident(self, lc_ident):
        """Sets the lc_ident of this BillTextContent.


        :param lc_ident: The lc_ident of this BillTextContent.
        :type lc_ident: str
        """

        self._lc_ident = lc_ident
