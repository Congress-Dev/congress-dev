from unittest import TestCase
from billparser.actions import determine_action, ActionType


class TestDetermineAction(TestCase):
    def test_strike_multiple(self):
        text = """by striking "Attorney General" each place such term appears and inserting "Secretary of Homeland Security"; and"""
        result = determine_action(text)
        self.assertIn(ActionType.STRIKE_TEXT_MULTIPLE, result)
        self.assertEqual(
            result[ActionType.STRIKE_TEXT_MULTIPLE]["to_remove_text"],
            "Attorney General",
        )

    def test_insert_section(self):
        text = """by adding at the end the following:"""
        result = determine_action(text)
        self.assertIn(ActionType.INSERT_END, result)

    def test_insert_end(self):
        text = """Section 242(f) of the Immigration and Nationality Act (8 U.S.C. 1252(f)) is amended by adding at the end following:"""
        result = determine_action(text)
        self.assertIn(ActionType.INSERT_END, result)


class TestEnactmentDates(TestCase):
    def test_not_later_days(self):
        text = """not later than 180 days after the date of enactment of this Act"""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "180")
        self.assertEqual(result["unit"], "days")

    def test_not_later_full_title(self):
        text = """Not later than 60 days after the date of enactment of the Requiring Effective Management and Oversight of Teleworking Employees Act"""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "60")
        self.assertEqual(result["unit"], "days")

    def test_beginning_days(self):
        text = """Beginning on the date that is 180 days after the date of enactment of this Act"""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "180")
        self.assertEqual(result["unit"], "days")

    def test_more_verbiage(self):
        text = """Not later than 120 days after the date of the enactment of this Act"""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "120")
        self.assertEqual(result["unit"], "days")

    def test_sunset(self):
        text = """This Act shall cease to have any force or effect beginning on the date that is 5 years after the date of the enactment of this Act."""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "5")
        self.assertEqual(result["unit"], "years")

    def test_take_effect(self):
        text = """The amendments made by this section shall take effect 90 days after the date of the enactment of this Act."""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "90")
        self.assertEqual(result["unit"], "days")
