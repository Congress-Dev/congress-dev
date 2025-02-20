from unittest import TestCase
from lxml import etree
from billparser.utils.cite_parser import (
    parse_action_for_cite,
    parse_text_for_cite,
    extract_usc_cite,
)


class TestParseTextForCite(TestCase):
    def test_119_s_21_title_of_code(self):
        text = """Section 6506(d) of title 5, United States Code, is amended-"""
        res = parse_text_for_cite(text)
        self.assertEqual(len(res), 1)
        cite = res[0]
        self.assertEqual(cite["cite"], "/us/usc/t5/s6506/d")

    def test_random(self):
        text = """Paragraph (6) of section 106 of title 17, United States Code, is amended to read as follows:"""
        res = parse_text_for_cite(text)
        self.assertEqual(len(res), 1)
        cite = res[0]
        self.assertEqual(cite["cite"], "/us/usc/t17/s106/6")

    def test_118_hr_5__is_amended(self):
        text = "Section 1111(g)(2) of the Elementary and Secondary Education Act of 1965 (20 U.S.C. 6311(g)(2)) is amended-"
        res = parse_text_for_cite(text)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["cite"], "/us/usc/t20/s6311/g/2")

    def test_119_hr_22__double_paren(self):
        text = """in subsection (a)(1), by striking "Each State motor vehicle driver's license application" and inserting "Subject to the requirements under section 8(j), each State motor vehicle driver's license application"""
        res = parse_text_for_cite(text)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["cite"], "/a/1")


class TestExtractUSCCite(TestCase):
    def test_118_hr_5__is_amended(self):
        text = "Section 1111(g)(2) of the Elementary and Secondary Education Act of 1965 (20 U.S.C. 6311(g)(2)) is amended-"
        cite = extract_usc_cite(text)
        self.assertEqual(cite, "/us/usc/t20/s6311/g/2")

    def test_118_hr_5__multi_paren(self):
        # The double parens are annoying af, had to switch to a non greedy regex and use the end of sentence matcher
        text = """Section 444(f) of the General Education Provisions Act (20 U.S.C. 1232g) (also known as the "Family Educational Rights and Privacy Act of 1974") (20 U.S.C. 1232g(f)) is amended by adding at the end the following: "The Secretary shall comply with the reporting requirement under section 445(e)(2)(C)(ii) with respect to the enforcement actions taken under this subsection to ensure compliance with this section."."""
        cite = extract_usc_cite(text)
        self.assertEqual(cite, "/us/usc/t20/s1232g")

    def test_118_hr_5568__weird(self):
        text = """Section 2107(e)(1)(J) of the Social Security Act (42 U.S.C. 1397gg(e)(1)(J)), as inserted by section 9822 of the American Rescue Plan Act of 2021 (Public Law 117-2), is amended to read as follows:"""
        cite = extract_usc_cite(text)
        self.assertEqual(cite, "/us/usc/t42/s1397gg/e/1/J")

    def test_119_hr_471_parens(self):
        text = """in section 603(c)(2)(B) (16 U.S.C. 6591b(c)(2)(B)), by striking "Fire Regime Groups I, II, or III" and inserting "Fire Regime I, Fire Regime II, Fire Regime III, Fire Regime IV, or Fire Regime V"""
        cite = extract_usc_cite(text)
        self.assertEqual(cite, "/us/usc/t16/s6591b/c/2/B")
