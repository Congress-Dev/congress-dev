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