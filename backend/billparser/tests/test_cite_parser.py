from unittest import TestCase
from lxml import etree
from billparser.utils.cite_parser import parse_action_for_cite

class TestParseActionForCite(TestCase):
    def test_118_hr_5968(self):
        cite = {
            "parent": "5968",
            "enum": "5968/s2",
            "lxml_path": "/bill/legis-body/section[2]",
            "text": "Notwithstanding any other provision of law, amounts made available to carry out the Department of Homeland Security's Shelter and Services Program shall be made available to the Department of State to carry out section 4(b)(2)(A)(ii) of the State Department Basic Authorities Act of 1956 (22 U.S.C. 2671(b)(2)(A)(ii)), as amended by section 1(1). ",
            "text_element": etree.fromstring("""<text display-inline="no-display-inline">Notwithstanding any other provision of law, amounts made available to carry out the Department of Homeland Security’s Shelter and Services Program shall be made available to the Department of State to carry out section 4(b)(2)(A)(ii) of the State Department Basic Authorities Act of 1956 (<external-xref legal-doc="usc" parsable-cite="usc/22/2671">22 U.S.C. 2671(b)(2)(A)(ii)</external-xref>), as amended by section 1(1). </text>"""),
            "amended": True,
            "next": "",
        }
        res = parse_action_for_cite(cite)
        self.assertEqual(res, "/us/usc/t22/s2671/b/2/A/ii")

    def test_118_hr_11_ih(self):
        elem = """
            <text display-inline="yes-display-inline">
                Section 5(c)(2)(B)(ii) of the National Voter Registration Act of 1993 (
                <external-xref legal-doc="usc" parsable-cite="usc/52/20504">
                    52 U.S.C. 20504(c)(2)(B)(ii)
                </external-xref>
                ) is amended by striking the semicolon at the end and inserting the following:
                <quote>
                    , and to the extent that the application requires the applicant to provide a social security number, may not require the applicant to provide more than the last 4 digits of such number;
                </quote>
                .
            </text>
        """
        elem = etree.fromstring(elem)
        cite = {
            "parent": "5968",
            "enum": "5968/s2",
            "lxml_path": "/bill/legis-body/section[2]",
            "text": elem.text,
            "text_element": elem,
            "amended": True,
            "next": "",
        }
        res = parse_action_for_cite(cite)
        self.assertEqual(res, "/us/usc/t52/s20504/c/2/B/ii")

    def test_118_s_8_is(self):
        elem = """
            <text>
                Clause (i) of section 1402(c)(1)(B) of such Act (
                <external-xref legal-doc="usc" parsable-cite="usc/42/18071">
                    42 U.S.C. 18071(c)(1)(B)
                </external-xref>
                ) is amended to read as follows:
            </text>
        """
        elem = etree.fromstring(elem)
        cite = {
            "parent": "5968",
            "enum": "5968/s2",
            "lxml_path": "/bill/legis-body/section[2]",
            "text": elem.text,
            "text_element": elem,
            "amended": True,
            "next": "",
        }
        res = parse_action_for_cite(cite)
        self.assertEqual(res, "/us/usc/t42/s18071/c/1/B/i")
    def test_118_s_8_is_2(self):
        elem = """
        				<text>
					Section 1402 of the Patient Protection and Affordable Care Act (
					<external-xref legal-doc="usc" parsable-cite="usc/42/18071">
						42 U.S.C. 18071
					</external-xref>
					) is amended by adding at the end the following new subsection:
				</text>
        """
        elem = etree.fromstring(elem)
        cite = {
            "parent": "5968",
            "enum": "5968/s2",
            "lxml_path": "/bill/legis-body/section[2]",
            "text": elem.text,
            "text_element": elem,
            "amended": True,
            "next": "",
        }
        res = parse_action_for_cite(cite)
        self.assertEqual(res, "/us/usc/t42/s18071")
    def test_118_s_8_is_parent(self):
        elem = """
        		<text>
					Section 1402 of such act is amended by adding at the end the following new subsection:
				</text>
        """
        elem = etree.fromstring(elem)
        cite = {
            "parent": "5968",
            "enum": "5968/s2",
            "lxml_path": "/bill/legis-body/section[2]",
            "text": elem.text,
            "text_element": elem,
            "amended": True,
            "next": "",
        }
        res = parse_action_for_cite(cite, parent_cite="/us/usc/t42/s18071")
        self.assertEqual(res, "/us/usc/t42/s18071/1402")