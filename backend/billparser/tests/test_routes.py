from unittest import TestCase, mock
import json
from billparser.__main__ import (
    bills,
    app,
    bill_content,
    bill_content_tree,
    titles,
    versions,
    revisions,
    version,
    latest_sections,
    sections,
    contents,
)

from billparser.db.models import (
    USCChapter,
    USCSection,
    USCContent,
    USCContentDiff,
    Version,
    Legislation,
    LegislationVersion,
    LegislationContent,
    LegislationVersionEnum,
    LegislationChamber,
    LegislationType,
)

# This is to ensure that the return values are the same
# No matter what, these return values shouldn't change, or the frontend
# Will need to change
class TestRoutes(TestCase):
    @mock.patch("billparser.__main__.get_bills", return_value=[])
    def test_bills_no_version(self, mock_get_bills):
        """
            Should be returning a dict where the key is the bill, and the value is the bill metadata
        """
        mock_get_bills.return_value = [
            Legislation(
                legislation_id=1,
                legislation_type=LegislationType.Bill,
                chamber=LegislationChamber.House,
                title="Test House Bill",
                number=1
            ),
            Legislation(
                legislation_id=2,
                legislation_type=LegislationType.Bill,
                chamber=LegislationChamber.Senate,
                title="Test Senate Bill",
                number=5
            ),
        ]
        with app.app.test_request_context():
            resp = bills()
            self.assertEqual(
                json.dumps(
                    {
                        "H-1": {
                            "bill_id": "1",
                            "chamber": "House",
                            "bill_type": "BillTypes.Bill",
                            "bill_number": "1",
                            "bill_title": "Test House Bill",
                            "versions": [],
                        },
                        "S-5": {
                            "bill_id": "2",
                            "chamber": "Senate",
                            "bill_type": "BillTypes.Bill",
                            "bill_number": "5",
                            "bill_title": "Test Senate Bill",
                            "versions": [],
                        },
                    }
                ),
                resp,
            )

    @mock.patch("billparser.__main__.get_bills", return_value=[])
    def test_bills_with_version(self, mock_get_bills):
        """
            Should be returning a dict where the key is the bill, and the value is the bill metadata
            Should also include the given bill versions for the bill
        """


        mock_get_bills.return_value = [
            Legislation(
                legislation_id=1,
                legislation_type=LegislationType.Bill,
                chamber=LegislationChamber.House,
                title="Test House Bill",
                number=1,
                versions=[
                    LegislationVersion(
                        legislation_version_id=1,
                        legislation_id=1,
                        legislation_version=LegislationVersionEnum.IH,
                    )
                ],
            ),
            Legislation(
                legislation_id=2,
                legislation_type=LegislationType.Bill,
                chamber=LegislationChamber.Senate,
                title="Test Senate Bill",
                number=5,
                versions=[
                    LegislationVersion(
                        legislation_version_id=2,
                        legislation_id=2,
                        legislation_version=LegislationVersionEnum.IS,
                    )
                ],
            ),
        ]
        with app.app.test_request_context():
            resp = bills()
            self.assertEqual(
                json.dumps(
                    {
                        "H-1": {
                            "bill_id": "1",
                            "chamber": "House",
                            "bill_type": "BillTypes.Bill",
                            "bill_number": "1",
                            "bill_title": "Test House Bill",
                            "versions": [
                                {
                                    "bill_version_id": "1",
                                    "bill_id": "1",
                                    "bill_version": "ih",
                                    # "base_version_id": "1", # This was removed in the translation
                                }
                            ],
                        },
                        "S-5": {
                            "bill_id": "2",
                            "chamber": "Senate",
                            "bill_type": "BillTypes.Bill",
                            "bill_number": "5",
                            "bill_title": "Test Senate Bill",
                            "versions": [
                                {
                                    "bill_version_id": "2",
                                    "bill_id": "2",
                                    "bill_version": "is",
                                    # "base_version_id": "1", # This was removed in the translation
                                }
                            ],
                        },
                    }
                ),
                resp,
                resp,
            )

    @mock.patch("billparser.__main__.get_bill_contents", return_value=[])
    def test_bill_content_1(self, mock_get_bill_contents):
        """
            Should return the bill content objects
        """
        mock_get_bill_contents.return_value = [
            LegislationContent(
                legislation_content_id=1,
                parent_id=None,
                order_number=0,
                section_display="SS 1.)",
                heading="Test heading",
                content_str="Test content",
                legislation_version_id=1,
                content_type="section",
                action_parse=[],
            ),
        ]
        with app.app.test_request_context():
            resp = bill_content("1")
            self.assertEqual(
                json.dumps(
                    [
                        {
                            "bill_content_id": 1,
                            "content_type": "section",
                            "order": 0,
                            # "number": "1", # Removed
                            "display": "SS 1.)",
                            "heading": "Test heading",
                            "content": "Test content",
                            "version": "1",
                        }
                    ]
                ),
                resp,
                resp,
            )

    @mock.patch("billparser.__main__.get_bill_contents", return_value=[])
    def test_bill_content_2(self, mock_get_bill_contents):
        """
            Should return the bill content objects, multiple contents
        """
        self.maxDiff = None
        mock_get_bill_contents.return_value = [
            LegislationContent(
                legislation_content_id=1,
                parent_id=None,
                order_number=0,
                section_display="SS 1.)",
                heading="Test heading",
                content_str="Test content",
                legislation_version_id=1,
                content_type="section",
                action_parse=[],
            ),
            LegislationContent(
                legislation_content_id=2,
                parent_id="1",
                order_number=0,
                section_display="a.)",
                heading="",
                content_str="Test subcontent",
                legislation_version_id=1,
                content_type="legis-body",
                action_parse=[],
            ),
        ]
        with app.app.test_request_context():
            resp = bill_content("1")
            self.assertEqual(
                json.dumps(
                    [
                        {
                            "bill_content_id": 1,
                            "content_type": "section",
                            "order": 0,
                            # "number": "1", # Removed
                            "display": "SS 1.)",
                            "heading": "Test heading",
                            "content": "Test content",
                            "version": "1",
                        },
                        {
                            "bill_content_id": 2,
                            "content_type": "legis-body",
                            "order": 0,
                            "parent": "1",
                            # "number": "a", # Removed
                            "display": "a.)",
                            "heading": "",
                            "content": "Test subcontent",
                            "version": "1",
                        },
                    ]
                ),
                resp,
                resp,
            )

    @mock.patch("billparser.__main__.get_bill_metadata", return_value=[])
    @mock.patch("billparser.__main__.get_bill_contents", return_value=[])
    def test_bill_content_tree_1(self, mock_get_bill_contents, mock_get_bill_metadata):
        """
            Should return the bill content objects, and metadata
        """
        mock_get_bill_metadata.return_value = {
            "chamber": "House",
            "number": "12",
            "version": "1",
        }
        mock_get_bill_contents.return_value = [
            LegislationContent(
                legislation_content_id=1,
                parent_id=None,
                order_number=0,
                section_display="SS 1.)",
                heading="Test heading",
                content_str="Test content",
                legislation_version_id=1,
                content_type="section",
                action_parse=[],
            ),
            LegislationContent(
                legislation_content_id=2,
                parent_id=1,
                order_number=0,
                section_display="a.)",
                heading="",
                content_str="Test subcontent",
                legislation_version_id=1,
                content_type="legis-body",
                action_parse=[],
            ),
        ]
        with app.app.test_request_context():
            resp = bill_content_tree("1")
            self.assertEqual(
                json.dumps(
                    {
                        "content": {
                            "bill_content_id": 1,
                            "content_type": "section",
                            "order": 0,
                            #"number": "1", # Removed
                            "display": "SS 1.)",
                            "heading": "Test heading",
                            "content": "Test content",
                            "version": "1",
                            "child": [
                                {
                                    "bill_content_id": 2,
                                    "content_type": "legis-body",
                                    "order": 0,
                                    "parent": 1,
                                    # "number": "a", # Removed
                                    "display": "a.)",
                                    "heading": "",
                                    "content": "Test subcontent",
                                    "version": "1",
                                    "child": [],
                                }
                            ],
                        },
                        "metadata": {
                            "chamber": "House",
                            "number": "12",
                            "version": "1",
                        },
                    }
                ),
                resp,
                resp,
            )

    @mock.patch("billparser.__main__.get_chapters", return_value=[])
    def test_chapters(self, mock_get_chapters):
        """
            Should return the chapter objects
        """
        mock_get_chapters.return_value = [
            USCChapter(
                usc_chapter_id=1,
                usc_ident="/usc/1",
                short_title="01",
                document="usc",
                version_id=1,
            )
        ]
        with app.app.test_request_context():
            resp = titles()
            self.assertEqual(
                json.dumps(
                    [{"chapter_id": 1, "ident": "/usc/1", "number": "01", "version": 1}]
                ),
                resp,
                resp,
            )

    @mock.patch("billparser.__main__.get_versions", return_value=[])
    def test_versions(self, mock_get_versions):
        """
            Should return the version objects
        """
        mock_get_versions.return_value = [
            Version(version_id=1, base_id=1)
        ]
        with app.app.test_request_context():
            resp = versions()
            self.assertEqual(
                json.dumps([{"version_id": 1, "title": "Legacy Title", "base_id": 1}]),
                resp,
                resp,
            )

    @mock.patch("billparser.__main__.get_revisions", return_value=[])
    def test_revisions(self, mock_get_versions):
        """
            Should return the version objects without a base id
        """
        mock_get_versions.return_value = [
            Version(
                version_id=1, base_id=None
            )
        ]
        with app.app.test_request_context():
            resp = revisions()
            self.assertEqual(
                json.dumps([{"version_id": 1, "title": "Legacy Title"}]), resp, resp,
            )

    @mock.patch("billparser.__main__.get_content_versions", return_value=[])
    @mock.patch("billparser.__main__.get_diffs", return_value=[])
    def test_get_version(self, mock_get_diffs, mock_get_content_versions):
        """
            Should return the version objects without a base id
        """
        mock_get_content_versions.return_value = [
            USCContent(
                usc_content_id=1,
                usc_section_id=1,
                parent_id=None,
                usc_ident="/usc/s1/1",
                usc_guid="1-2-3",
                number="1",
                section_display="S 1.)",
                heading="Test - heading",
                content_str="content - str",
                version_id=1,
            )
        ]
        mock_get_diffs.return_value = [
            USCContentDiff(
                usc_content_diff_id=1,
                usc_chapter_id=1,
                usc_section_id=1,
                usc_content_id=1,
                order_number=0,
                number="1",
                section_display="test",
                heading="test - heading",
                content_str="test - content",
                version_id=1,
            )
        ]
        with app.app.test_request_context(json={"version": 1}):
            resp = version()
            self.assertEqual(
                json.dumps(
                    {
                        "diffs": [
                            {
                                "id": 1,
                                "content_id": 1,
                                "section_id": 1,
                                "chapter_id": 1,
                                "order": 0,
                                "number": "1",
                                "display": "test",
                                "heading": "test - heading",
                                "content": "test - content",
                                "version": 1,
                            }
                        ],
                        "contents": [
                            {
                                "content_id": 1,
                                "section_id": 1,
                                "ident": "/usc/s1/1",
                                "number": "1",
                                "display": "S 1.)",
                                "heading": "Test - heading",
                                "content": "content - str",
                                "version": 1,
                            }
                        ],
                    }
                ),
                resp,
                resp,
            )

    @mock.patch("billparser.__main__.get_latest_sections", return_value=[])
    def test_latest_sections(self, mock_get_sections):
        """
            Should return the section objects
        """
        mock_get_sections.return_value = [
            USCSection(
                usc_section_id=1,
                usc_ident="/usc/01/s1",
                number="1",
                section_display="S 1.)",
                heading="Test - Heading",
                usc_chapter_id=1,
                version_id=1,
            )
        ]

        with app.app.test_request_context():
            resp = latest_sections("1")
            self.assertEqual(
                json.dumps(
                    [
                        {
                            "section_id": 1,
                            "ident": "/usc/01/s1",
                            "number": "1",
                            "display": "S 1.)",
                            "heading": "Test - Heading",
                            "chapter_id": 1,
                            "version": 1,
                        }
                    ]
                ),
                resp,
                resp,
            )

    @mock.patch("billparser.__main__.get_latest_sections", return_value=[])
    def test_latest_sections(self, mock_get_sections):
        """
            Should return the section objects
        """
        mock_get_sections.return_value = [
            USCSection(
                usc_section_id=1,
                usc_ident="/usc/01/s1",
                number="1",
                section_display="S 1.)",
                heading="Test - Heading",
                usc_chapter_id=1,
                version_id=1,
            )
        ]

        with app.app.test_request_context():
            resp = latest_sections("1")
            self.assertEqual(
                json.dumps(
                    [
                        {
                            "section_id": 1,
                            "ident": "/usc/01/s1",
                            "number": "1",
                            "display": "S 1.)",
                            "heading": "Test - Heading",
                            "chapter_id": 1,
                            "version": 1,
                        }
                    ]
                ),
                resp,
                resp,
            )

    @mock.patch(
        "billparser.__main__.get_latest_base", return_value=Version(version_id=1)
    )
    @mock.patch("billparser.__main__.get_sections", return_value=[])
    def test_sections(self, mock_get_sections, mock_get_latest_base):
        """
            Should return the section objects
        """
        mock_get_sections.return_value = [
            USCSection(
                usc_section_id=1,
                usc_ident="/usc/01/s1",
                number="1",
                section_display="S 1.)",
                heading="Test - Heading",
                usc_chapter_id=1,
                version_id=1,
            )
        ]

        with app.app.test_request_context():
            resp = sections("1")
            self.assertEqual(
                json.dumps(
                    [
                        {
                            "section_id": 1,
                            "ident": "/usc/01/s1",
                            "number": "1",
                            "display": "S 1.)",
                            "heading": "Test - Heading",
                            "chapter_id": 1,
                            "version": 1,
                        }
                    ]
                ),
                resp,
                resp,
            )

    @mock.patch(
        "billparser.__main__.get_latest_base", return_value=Version(version_id=1)
    )
    @mock.patch("billparser.__main__.get_content", return_value=[])
    def test_contents(self, mock_get_content, mock_get_latest_base):
        """
            Should return the content objects
        """
        mock_get_content.return_value = [
            USCContent(
                usc_content_id=1,
                usc_section_id=1,
                parent_id=None,
                order_number=0,
                usc_ident="/usc/01/s1",
                usc_guid="1-2-3",
                number="1",
                section_display="S 1.)",
                heading="Test - Heading",
                content_str="Content - Str",
                version_id=1,
                content_type="legis-body",
            )
        ]

        with app.app.test_request_context():
            resp = contents("1")
            self.assertEqual(
                json.dumps(
                    [
                        {
                            "content_id": 1,
                            "content_type": "legis-body",
                            "section_id": 1,
                            "order": 0,
                            "ident": "/usc/01/s1",
                            "number": "1",
                            "display": "S 1.)",
                            "heading": "Test - Heading",
                            "content": "Content - Str",
                            "version": 1,
                        }
                    ]
                ),
                resp,
                resp,
            )

