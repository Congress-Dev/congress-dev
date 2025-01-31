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
