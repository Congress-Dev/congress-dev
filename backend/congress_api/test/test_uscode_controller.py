# coding: utf-8

from __future__ import absolute_import

import unittest

from congress_api.test import BaseTestCase


class TestUscodeController(BaseTestCase):
    """UscodeController integration test stubs"""

    def test_get_usc_release_sections(self):
        """Test case for get_usc_release_sections

        Your GET endpoint
        """
        query_string = [("page", 1), ("pageSize", 1000)]
        headers = {
            "Accept": "application/json",
        }
        response = self.client.open(
            "/usc/{release_vers}/{short_title}/sections".format(
                release_vers="release_vers_example", short_title="short_title_example"
            ),
            method="GET",
            headers=headers,
            query_string=query_string,
        )
        self.assert200(response, "Response body is : " + response.data.decode("utf-8"))

    def test_get_usc_release_text(self):
        """Test case for get_usc_release_text

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

    def test_get_usc_release_titles(self):
        """Test case for get_usc_release_titles

        Your GET endpoint
        """
        headers = {
            "Accept": "application/json",
        }
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
