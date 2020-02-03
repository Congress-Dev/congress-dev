# coding: utf-8

from __future__ import absolute_import

import unittest

from congress_api.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

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

    def test_get_usc_release_vers_short_tile_section_number_text(self):
        """Test case for get_usc_release_vers_short_tile_section_number_text

        Your GET endpoint
        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/usc/{release_vers}/{short_tile}/{section_number}/text".format(
                release_vers="release_vers_example",
                short_tile="short_tile_example",
                section_number="section_number_example",
            ),
            method="GET",
            headers=headers,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_usc_release_vers_short_title_sections(self):
        """Test case for get_usc_release_vers_short_title_sections

        Your GET endpoint
        """
        query_string = [("page", 0), ("pageSize", 5000)]
        headers = {}
        response = self.client.open(
            "/usc/{release_vers}/{short_title}/sections".format(
                release_vers="release_vers_example", short_title="short_title_example"
            ),
            method="GET",
            headers=headers,
            query_string=query_string,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_usc_release_vers_titles(self):
        """Test case for get_usc_release_vers_titles

        Your GET endpoint
        """
        headers = {}
        response = self.client.open(
            "/usc/{release_vers}/titles".format(release_vers="release_vers_example"),
            method="GET",
            headers=headers,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_usc_releases(self):
        """Test case for get_usc_releases

        Your GET endpoint
        """
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open("/usc/releases", method="GET", headers=headers)
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
