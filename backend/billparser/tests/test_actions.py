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

    def test_redesignate_subsection(self):
        text = "redesignating subsection (b) as subsection (c); and"
        result = determine_action(text)
        self.assertIn(ActionType.REDESIGNATE, result)
        action = result[ActionType.REDESIGNATE]
        self.assertEqual(action["target"], "subsection (b)")
        self.assertEqual(action["redesignation"], "subsection (c)")

    def test_insert_before_period(self):
        text = """in clause (i), by inserting before the period at the end the following ", and includes any crime that constitutes domestic violence, as such term is defined in section 40002(a) of the Violent Crime Control and Law Enforcement Act of 1994 (34 U.S.C. 12291(a)), regardless of whether the jurisdiction receives grant funding under that Act"; and"""
        result = determine_action(text)
        self.assertIn(ActionType.INSERT_TEXT_BEFORE, result)
        self.assertIn("period_at_end", result[ActionType.INSERT_TEXT_BEFORE])

    def test_long_short_title(self):
        text = """This Act may be cited as the "Requiring Effective Management and Oversight of Teleworking Employees Act" or the "REMOTE Act"."""
        result = determine_action(text)
        self.assertIn(ActionType.SHORT_TITLE, result)
        self.assertEqual(
            result[ActionType.SHORT_TITLE]["title"],
            "Requiring Effective Management and Oversight of Teleworking Employees Act",
        )
        self.assertEqual( result[ActionType.SHORT_TITLE]["short_title"], "REMOTE Act")


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

    def test_one_day(self):
        text = """This Act shall take effect one day after the date of enactment."""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["amount"], "1")
        self.assertEqual(result["unit"], "day")

    def test_amendments_take_effect_specific_date(self):
        text = """The amendments made by paragraph (1) shall take effect on July 1, 2026, and shall apply with respect to award year 2026-2027 and each subsequent award year, as determined under the Higher Education Act of 1965."""
        result = determine_action(text)
        self.assertIn(ActionType.EFFECTIVE_DATE, result)
        result = result[ActionType.EFFECTIVE_DATE]
        self.assertEqual(result["target"], "paragraph (1)")
        self.assertEqual(result["effective_date"], "July 1, 2026")
        self.assertEqual(result["amount"], "0")
        self.assertEqual(result["unit"], "days")


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


class TestRecission(TestCase):
    def test_recission_with_stat_ref(self):
        text = """The unobligated balances of amounts appropriated by section 21001(a) of Public Law 117-169 (136 Stat. 2015) are rescinded."""
        result = determine_action(text)
        self.assertIn(ActionType.RECISSION, result)
        result = result[ActionType.RECISSION]
        self.assertEqual(result["section_ref"], "section 21001(a) of Public Law 117-169")
        self.assertEqual(result["stat_ref"], "136 Stat. 2015")
        self.assertIn("unobligated balances", result["target"])

    def test_recission_without_stat_ref(self):
        text = """The unobligated balances of amounts appropriated by section 5001 of Public Law 118-42 are rescinded."""
        result = determine_action(text)
        self.assertIn(ActionType.RECISSION, result)
        result = result[ActionType.RECISSION]
        self.assertEqual(result["section_ref"], "section 5001 of Public Law 118-42")
        self.assertIsNone(result.get("stat_ref"))
        self.assertIn("unobligated balances", result["target"])


class TestSunset(TestCase):
    def test_sunset_cease_to_have_effect_on_date(self):
        text = """This Act shall cease to have effect on December 31, 2025."""
        result = determine_action(text)
        self.assertIn(ActionType.SUNSET, result)
        result = result[ActionType.SUNSET]
        self.assertEqual(result["target"], "This Act")
        self.assertEqual(result["sunset_date"], "December 31, 2025")

    def test_sunset_expire_on_date(self):
        text = """The program shall expire on September 30, 2026."""
        result = determine_action(text)
        self.assertIn(ActionType.SUNSET, result)
        result = result[ActionType.SUNSET]
        self.assertEqual(result["target"], "The program")
        self.assertEqual(result["sunset_date"], "September 30, 2026")

    def test_sunset_terminate_on_date(self):
        text = """The temporary authority shall terminate on January 1, 2027."""
        result = determine_action(text)
        self.assertIn(ActionType.SUNSET, result)
        result = result[ActionType.SUNSET]
        self.assertEqual(result["target"], "The temporary authority")
        self.assertEqual(result["sunset_date"], "January 1, 2027")

    def test_sunset_with_time_period_after_trigger(self):
        text = """The pilot program shall cease to be effective 3 years after the date of enactment of this Act."""
        result = determine_action(text)
        self.assertIn(ActionType.SUNSET, result)
        result = result[ActionType.SUNSET]
        self.assertEqual(result["target"], "The pilot program")
        self.assertEqual(result["amount"], "3")
        self.assertEqual(result["unit"], "years")
        self.assertEqual(result["trigger_date"], "the date of enactment of this Act")

    @skip("Not implemented")
    def test_sunset_authority_provided_by(self):
        text = """The authority provided by this section shall expire on December 31, 2028."""
        result = determine_action(text)
        self.assertIn(ActionType.SUNSET, result)
        result = result[ActionType.SUNSET]
        self.assertEqual(result["target"], "this section")
        self.assertEqual(result["sunset_date"], "December 31, 2028")

    @skip("Not implemented")
    def test_sunset_authority_under(self):
        text = """The authority under section 123 shall cease to have effect on June 30, 2025."""
        result = determine_action(text)
        self.assertIn(ActionType.SUNSET, result)
        result = result[ActionType.SUNSET]
        self.assertEqual(result["target"], "section 123")
        self.assertEqual(result["sunset_date"], "June 30, 2025")

    def test_sunset_with_days_after_trigger(self):
        text = """The emergency powers shall terminate 90 days after the President declares the emergency over."""
        result = determine_action(text)
        self.assertIn(ActionType.SUNSET, result)
        result = result[ActionType.SUNSET]
        self.assertEqual(result["target"], "The emergency powers")
        self.assertEqual(result["amount"], "90")
        self.assertEqual(result["unit"], "days")
        self.assertEqual(result["trigger_date"], "the President declares the emergency over")
