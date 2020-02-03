from unittest import TestCase, mock, skipUnless


from congress_api.db.chamber_queries import (
    get_chamber_summary_obj,
    get_chamber_bills_list,
    search_legislation,
)

DB_MOCKED = False


class TestGetChamberSummary(TestCase):
    def test_raises_type_error_for_session(self):
        with self.assertRaises(TypeError):
            get_chamber_summary_obj("not int", "House")

    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_returns_none_for_no_results(self):
        pass

    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_returns_counts_for_bills(self):
        pass


class TestGetChamberBillList(TestCase):
    def test_raises_type_error_for_session(self):
        with self.assertRaises(TypeError):
            get_chamber_bills_list("not int", "House", 25, 1)

    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_computes_limits_and_offsets(self):
        pass

    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_returns_details_for_bills(self):
        pass


class TestSearchLegislation(TestCase):
    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_searches_given_congress(self):
        pass

    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_searches_given_chambers_house(self):
        pass

    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_searches_given_chambers_senate(self):
        pass

    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_searches_given_chambers_both(self):
        pass

    @skipUnless(DB_MOCKED, "Need to mock SQLAlchemy")
    def test_searches_given_bill_statuses(self):
        pass
