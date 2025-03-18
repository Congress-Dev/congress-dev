from unittest import TestCase, skip
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

    def test_insert_text_end(self):
        text = """by adding at the end the following: "For purposes of the preceding sentence, the term "non-invasive" means, with respect to a diagnostic device, that the device does not penetrate the skin or any other membrane of the body, is not inserted or implanted into the body, causes no more than ephemeral compression or temperature changes to in situ bodily tissues, and does not subject bodily tissues to ionizing radiation."."""
        result = determine_action(text)
        self.assertIn(ActionType.INSERT_TEXT_END, result)

    def test_insert_subsection(self):
        text = """by adding at the end the following new subsection:"""
        result = determine_action(text)
        self.assertIn(ActionType.INSERT_END, result)

    def test_strike_period(self):
        text = """by striking the period at the end and inserting "; and"."""
        result = determine_action(text)
        self.assertIn(ActionType.STRIKE_END, result)
        self.assertIn("remove_period", result[ActionType.STRIKE_END])

    def test_strike_comma(self):
        text = """in subparagraph (D), by striking the comma at the end and inserting ", or"; and"""
        result = determine_action(text)
        self.assertIn(ActionType.STRIKE_END, result)
        self.assertIn("remove_comma", result[ActionType.STRIKE_END])

    def test_insert_section_after(self):
        text = """inserting after subsection (a) the following:"""
        result = determine_action(text)
        self.assertIn(ActionType.INSERT_SECTION_AFTER, result)

    def test_repeal(self):
        text = """Section 3 of the Uniform Time Act of 1966 (15 U.S.C. 260a) is hereby repealed."""
        result = determine_action(text)
        self.assertIn(ActionType.REPEAL, result)
        

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

    def test_hours(self):
        text = """Not later than 24 hours after the date of enactment of this Act"""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "24")
        self.assertEqual(result["unit"], "hours")

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

    @skip("Not implemented")
    def test_fiscal_year(self):
        text = """This Act shall take effect on the 1st day of the 1st fiscal year that begins after the date of the enactment of this Act."""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "1")
        self.assertEqual(result["unit"], "fiscal year")

    def test_same_day(self):
        text = "Effective on the date of enactment of this Act"
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "0")
        self.assertEqual(result["unit"], "days")

    def test_same_date(self):
        text = """Effective beginning on the date of the enactment of this Act"""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "0")
        self.assertEqual(result["unit"], "days")

    def test_cease(self):
        text = """The court described in subsection (a) shall cease to exist for administrative purposes 2 years after the effective date of this Act."""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "2")
        self.assertEqual(result["unit"], "years")


class TestTermDefinitionRef(TestCase):
    def test_in_popular_name(self):
        text = """The term budget justification materials has the meaning given that term in section 3(b)(2)(A) of the Federal Funding Accountability and Transparency Act of 2006 (31 U.S.C. 6101 note)."""
        result = determine_action(text)
        self.assertIn(ActionType.TERM_DEFINITION_REF, result)
        result = result[ActionType.TERM_DEFINITION_REF]
        self.assertEqual(result["term"], "budget justification materials")


class TestTermDefSection(TestCase):
    def test_regular(self):
        text = """As used in this Act, the term covered device-"""
        result = determine_action(text)
        self.assertIn(ActionType.TERM_DEFINITION_SECTION, result)
        result = result[ActionType.TERM_DEFINITION_SECTION]
        self.assertEqual(result["term"], "covered device")
