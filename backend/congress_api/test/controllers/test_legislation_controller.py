# coding: utf-8

from __future__ import absolute_import

import unittest


from congress_api.test.controllers import BaseTestCase


class TestLegislationController(BaseTestCase):
    """LegislationController integration test stubs"""

    def test_get_bill_summary(self):
        """Test case for get_bill_summary


        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/{session}/{chamber_bil}/{bill}".format(
                session="116", chamber="chamber_example", bill="bill_example"
            ),
            method="GET",
            headers=headers,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_bill_version_amdts(self):
        """Test case for get_bill_version_amdts


        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/{session}/{chamber_bil}/{bill}/{base_version}/amendments/{new_version}".format(
                session="116",
                chamber="chamber_example",
                bill="bill_example",
                base_version="base_version_example",
                new_version="new_version_example",
            ),
            method="GET",
            headers=headers,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_bill_version_diffs(self):
        """Test case for get_bill_version_diffs


        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/{session}/{chamber_bil}/{bill}/{version}/diffs".format(
                session="116",
                chamber="chamber_example",
                bill="bill_example",
                version="version_example",
            ),
            method="GET",
            headers=headers,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_bill_version_summary(self):
        """Test case for get_bill_version_summary


        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/{session}/{chamber_bil}/{bill}/{version}/summary".format(
                session="116",
                chamber="chamber_example",
                bill="bill_example",
                version="version_example",
            ),
            method="GET",
            headers=headers,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_bill_version_text(self):
        """Test case for get_bill_version_text


        """
        query_string = [("include_parsed", False)]
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/{session}/{chamber_bil}/{bill}/{version}/text".format(
                session="116",
                chamber="chamber_example",
                bill="bill_example",
                version="version_example",
            ),
            method="GET",
            headers=headers,
            query_string=query_string,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_chamber_bills(self):
        """Test case for get_chamber_bills


        """
        query_string = [("page_size", 25), ("page", 1)]
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/{session}/{chamber_bill}".format(
                session="116", chamber="chamber_example"
            ),
            method="GET",
            headers=headers,
            query_string=query_string,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_chamber_summary(self):
        """Test case for get_chamber_summary

        Specific chamber
        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/{session}/{chamber}".format(
                session="116", chamber="chamber_example"
            ),
            method="GET",
            headers=headers,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_congress_search(self):
        """Test case for get_congress_search

        Your GET endpoint
        """
        query_string = [
            ("congress", "congress_example"),
            ("chamber", "chamber_example"),
            ("versions", "versions_example"),
            ("text", "text_example"),
            ("page", 1),
            ("pageSize", 25),
        ]
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/search", method="GET", headers=headers, query_string=query_string
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_session_summary(self):
        """Test case for get_session_summary

        Specific Session
        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/congress/{session}".format(session="116"), method="GET", headers=headers
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_sessions_summary(self):
        """Test case for get_sessions_summary

        Congress Sessions
        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open("/congress", method="GET", headers=headers)
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
