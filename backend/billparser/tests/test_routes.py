from unittest import TestCase, mock
import json
from billparser.__main__ import bills, app

from billparser.db.models import (
    Chapter,
    Section,
    Content,
    ContentDiff,
    Version,
    Bill,
    BillVersion,
    BillContent,
    BillTypes,
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
            Bill(
                bill_id=1,
                chamber="House",
                bill_type=BillTypes.Bill,
                bill_number=1,
                bill_title="Test House Bill",
            ),
            Bill(
                bill_id=2,
                chamber="Senate",
                bill_type=BillTypes.Bill,
                bill_number=5,
                bill_title="Test Senate Bill",
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
            Bill(
                bill_id=1,
                chamber="House",
                bill_type=BillTypes.Bill,
                bill_number=1,
                bill_title="Test House Bill",
                versions=[
                    BillVersion(
                        bill_version_id=1,
                        bill_id=1,
                        bill_version="ih",
                        base_version_id=1,
                    )
                ],
            ),
            Bill(
                bill_id=2,
                chamber="Senate",
                bill_type=BillTypes.Bill,
                bill_number=5,
                bill_title="Test Senate Bill",
                versions=[
                    BillVersion(
                        bill_version_id=2,
                        bill_id=2,
                        bill_version="is",
                        base_version_id=1,
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
                                    "base_version_id": "1",
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
                                    "base_version_id": "1",
                                }
                            ],
                        },
                    }
                ),
                resp,
                resp,
            )
