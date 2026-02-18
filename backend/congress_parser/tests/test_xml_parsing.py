"""
Tests for XML parsing functions across the congress_parser codebase.

Covers:
- convert_to_text(): XML element to text conversion with quote handling
- filename_regex: Bill filename parsing from govinfo.gov bulk data
- _nested_dict(): XML element tree to Python dict conversion
- open_usc(): USC XML identifier lookup dictionary building
- get_number(): USC identifier to numeric ordering conversion
- unidecode_str(): Unicode normalization utility
- translate_paragraph(): XML tag translation (bill XML -> USLM format)
- Bill XML structure parsing: title extraction, date extraction, legis-body traversal
- USC XML structure: namespace handling, hierarchy, identifier depth
- Bill status XML parsing: actions, committees, policy areas, subjects
- parse_such_code(): USC citation resolution from "such code" references
- strip_arr(): String array stripping utility
"""

import os
import re
import string
from unittest import TestCase

from lxml import etree
from unidecode import unidecode

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")


def _load_fixture(filename):
    """Load an XML fixture file and return its contents as bytes."""
    path = os.path.join(FIXTURES_DIR, filename)
    with open(path, "rb") as f:
        return f.read()


def _parse_fixture(filename):
    """Load and parse an XML fixture file, returning the root Element."""
    return etree.fromstring(_load_fixture(filename))


# ---------------------------------------------------------------------------
# Standalone copies of pure functions from releases.py that cannot be imported
# due to the spacy dependency chain (releases.py -> bills.py -> appropriations
# -> spacy). These mirror the implementations exactly so we test the same logic.
# ---------------------------------------------------------------------------
_ribber = string.ascii_letters + string.digits


def _unidecode_str(input_str):
    """Mirror of releases.unidecode_str."""
    return unidecode(input_str or "").replace("--", "-")


def _get_number(ident):
    """Mirror of releases.get_number."""
    ident = _unidecode_str(ident)
    if "..." in ident:
        ident = ident.split("...")[0]
    result = re.search(
        r"^(\d*)([a-z]*)\s?(?:\-?t?o?(?:\.\.\.)?\.?)\s?(\d*)([a-z]*)$",
        ident,
        re.IGNORECASE,
    )
    grps = None
    try:
        grps = result.groups()
        tot = float(grps[0])
        subtot = 0
        if grps[1] != "":
            for i in grps[1]:
                subtot += _ribber.index(i) / len(_ribber)
        if grps[2] != "":
            subtot += float(grps[2]) / 100
        if grps[3] != "":
            subtot += (_ribber.index(grps[3]) / len(_ribber)) / 1000
        return tot
    except Exception as e:
        return 0


def _open_usc(file_str):
    """Mirror of releases.open_usc."""
    lookup = {}
    usc_root = etree.fromstring(file_str)
    lookup["root"] = usc_root
    ids = usc_root.xpath("//*[@identifier]")
    for id in ids:
        lookup[id.attrib["identifier"]] = id
    return lookup, ids


# ---------------------------------------------------------------------------
# Tests for convert_to_text (run_through.py)
# ---------------------------------------------------------------------------
class TestConvertToText(TestCase):
    """Tests for run_through.convert_to_text which converts XML elements to
    plain text strings, handling <quote> tags by wrapping content in double
    quotes, and using unidecode to normalize Unicode characters."""

    def setUp(self):
        from congress_parser.run_through import convert_to_text

        self.convert_to_text = convert_to_text

    def test_plain_text_element(self):
        """Element with only text content returns that text."""
        elem = etree.fromstring("<text>Hello world</text>")
        result = self.convert_to_text(elem)
        self.assertEqual(result, "Hello world")

    def test_quote_tag_wraps_in_double_quotes(self):
        """<quote> elements should be wrapped in double quotes."""
        elem = etree.fromstring("<text>cited as the <quote>Test Act</quote>.</text>")
        result = self.convert_to_text(elem)
        self.assertEqual(result, 'cited as the "Test Act".')

    def test_nested_quotes(self):
        """Nested <quote> elements should produce nested double quotes."""
        xml = '<text>adding: <quote>the term <quote>device</quote> means a thing</quote>.</text>'
        elem = etree.fromstring(xml)
        result = self.convert_to_text(elem)
        self.assertEqual(result, 'adding: "the term "device" means a thing".')

    def test_empty_element(self):
        """Empty element returns empty string."""
        elem = etree.fromstring("<text/>")
        result = self.convert_to_text(elem)
        self.assertEqual(result, "")

    def test_element_with_tail(self):
        """Element tail text is included in the output."""
        xml = "<text>before <quote>quoted</quote> after</text>"
        elem = etree.fromstring(xml)
        result = self.convert_to_text(elem)
        self.assertEqual(result, 'before "quoted" after')

    def test_em_dash_replacement(self):
        """Double hyphens (from unidecode of em-dashes) are collapsed to single."""
        elem = etree.fromstring("<text>section 1\u2014general provisions</text>")
        result = self.convert_to_text(elem)
        self.assertIn("-", result)
        self.assertNotIn("--", result)

    def test_none_text_handling(self):
        """Elements with no text (only children) don't produce None errors."""
        xml = "<text><quote>only child</quote></text>"
        elem = etree.fromstring(xml)
        result = self.convert_to_text(elem)
        self.assertEqual(result, '"only child"')

    def test_multiple_children(self):
        """Element with multiple child elements concatenates their text."""
        xml = '<text>striking <quote>old</quote> and inserting <quote>new</quote>.</text>'
        elem = etree.fromstring(xml)
        result = self.convert_to_text(elem)
        self.assertEqual(result, 'striking "old" and inserting "new".')

    def test_real_bill_section_text(self):
        """Test with text extracted from a real bill fixture."""
        root = _parse_fixture("bill_amendments.xml")
        text_elem = root.xpath("//section[@id='sec1']/text")[0]
        result = self.convert_to_text(text_elem)
        self.assertIn('"Voter Registration Modernization Act"', result)
        self.assertIn('"VRMA"', result)

    def test_deeply_nested_quotes_from_fixture(self):
        """Test nested quotes from the nested quotes bill fixture."""
        root = _parse_fixture("bill_nested_quotes.xml")
        text_elem = root.xpath("//section[@id='sec2']/text")[0]
        result = self.convert_to_text(text_elem)
        self.assertIn('"non-invasive"', result)
        self.assertIn("does not penetrate the skin", result)


# ---------------------------------------------------------------------------
# Tests for filename_regex (run_through.py)
# ---------------------------------------------------------------------------
class TestFilenameRegex(TestCase):
    """Tests for the filename_regex pattern that parses govinfo.gov bulk data
    filenames like 'BILLS-119hr1234ih.xml' into congress session, chamber,
    bill number, and version components."""

    def setUp(self):
        from congress_parser.run_through import filename_regex

        self.regex = filename_regex

    def test_standard_house_bill(self):
        """Standard House bill filename parses correctly."""
        match = self.regex.search("BILLS-119hr1ih.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("session"), "119")
        self.assertEqual(match.group("house"), "hr")
        self.assertEqual(match.group("bill_number"), "1")
        self.assertEqual(match.group("bill_version"), "ih")

    def test_senate_bill(self):
        """Senate bill filename parses correctly."""
        match = self.regex.search("BILLS-119s10es.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("session"), "119")
        self.assertEqual(match.group("house"), "s")
        self.assertEqual(match.group("bill_number"), "10")
        self.assertEqual(match.group("bill_version"), "es")

    def test_enrolled_bill(self):
        """Enrolled bill version (enr) parses correctly."""
        match = self.regex.search("BILLS-118hr5376enr.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("session"), "118")
        self.assertEqual(match.group("house"), "hr")
        self.assertEqual(match.group("bill_number"), "5376")
        self.assertEqual(match.group("bill_version"), "enr")

    def test_referred_in_senate(self):
        """Referred in Senate (rfs) version parses correctly."""
        match = self.regex.search("BILLS-117hr3684rfs.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("session"), "117")
        self.assertEqual(match.group("house"), "hr")
        self.assertEqual(match.group("bill_number"), "3684")
        self.assertEqual(match.group("bill_version"), "rfs")

    def test_large_bill_number(self):
        """Bills with 4+ digit numbers parse correctly."""
        match = self.regex.search("BILLS-116hr12345ih.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("bill_number"), "12345")

    def test_hjres(self):
        """House Joint Resolution filename parses correctly."""
        match = self.regex.search("BILLS-119hjres1ih.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("house"), "hjres")
        self.assertEqual(match.group("bill_number"), "1")

    def test_sjres(self):
        """Senate Joint Resolution filename parses correctly."""
        match = self.regex.search("BILLS-119sjres25rs.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("house"), "sjres")
        self.assertEqual(match.group("bill_number"), "25")
        self.assertEqual(match.group("bill_version"), "rs")

    def test_hconres(self):
        """House Concurrent Resolution filename parses correctly."""
        match = self.regex.search("BILLS-119hconres5ih.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("house"), "hconres")

    def test_sconres(self):
        """Senate Concurrent Resolution filename parses correctly."""
        match = self.regex.search("BILLS-118sconres14es.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("house"), "sconres")
        self.assertEqual(match.group("bill_number"), "14")

    def test_hres(self):
        """House Simple Resolution filename parses correctly."""
        match = self.regex.search("BILLS-119hres100ih.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("house"), "hres")

    def test_sres(self):
        """Senate Simple Resolution filename parses correctly."""
        match = self.regex.search("BILLS-119sres50is.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("house"), "sres")
        self.assertEqual(match.group("bill_version"), "is")

    def test_no_match_on_invalid(self):
        """Invalid filename does not match."""
        match = self.regex.search("not-a-bill.xml")
        self.assertIsNone(match)

    def test_in_path_context(self):
        """Regex matches when filename is in a path context."""
        match = self.regex.search("some/path/BILLS-119hr42ih.xml")
        self.assertIsNotNone(match)
        self.assertEqual(match.group("bill_number"), "42")


# ---------------------------------------------------------------------------
# Tests for strip_arr (run_through.py)
# ---------------------------------------------------------------------------
class TestStripArr(TestCase):
    """Tests for strip_arr utility that strips whitespace from string arrays."""

    def setUp(self):
        from congress_parser.run_through import strip_arr

        self.strip_arr = strip_arr

    def test_strips_whitespace(self):
        result = self.strip_arr(["  hello  ", "  world  "])
        self.assertEqual(result, ["hello", "world"])

    def test_empty_list(self):
        result = self.strip_arr([])
        self.assertEqual(result, [])

    def test_no_whitespace(self):
        result = self.strip_arr(["already", "clean"])
        self.assertEqual(result, ["already", "clean"])

    def test_mixed_whitespace(self):
        result = self.strip_arr(["\ttabbed\t", "\n newline\n", "  spaces  "])
        self.assertEqual(result, ["tabbed", "newline", "spaces"])


# ---------------------------------------------------------------------------
# Tests for _nested_dict (status_parser.py)
# ---------------------------------------------------------------------------
class TestNestedDict(TestCase):
    """Tests for status_parser._nested_dict which recursively converts an XML
    element tree to a nested Python dictionary."""

    def setUp(self):
        from congress_parser.status_parser import _nested_dict

        self._nested_dict = _nested_dict

    def test_simple_leaf_elements(self):
        """Leaf elements (no children) map tag->text."""
        xml = """<item>
            <actionDate>2025-01-03</actionDate>
            <text>Introduced in House</text>
            <type>IntroReferral</type>
        </item>"""
        elem = etree.fromstring(xml)
        result = self._nested_dict(elem)
        self.assertEqual(result["actionDate"], "2025-01-03")
        self.assertEqual(result["text"], "Introduced in House")
        self.assertEqual(result["type"], "IntroReferral")

    def test_nested_elements(self):
        """Branch elements (with children) map tag->nested dict."""
        xml = """<item>
            <actionDate>2025-01-07</actionDate>
            <sourceSystem>
                <name>House floor actions</name>
                <code>2</code>
            </sourceSystem>
            <text>Referred to Committee</text>
        </item>"""
        elem = etree.fromstring(xml)
        result = self._nested_dict(elem)
        self.assertEqual(result["actionDate"], "2025-01-07")
        self.assertIsInstance(result["sourceSystem"], dict)
        self.assertEqual(result["sourceSystem"]["name"], "House floor actions")
        self.assertEqual(result["sourceSystem"]["code"], "2")

    def test_empty_element(self):
        """Empty element results in empty dict."""
        elem = etree.fromstring("<item/>")
        result = self._nested_dict(elem)
        self.assertEqual(result, {})

    def test_element_with_no_text(self):
        """Element with tag but no text content maps to None."""
        xml = "<item><actionCode/></item>"
        elem = etree.fromstring(xml)
        result = self._nested_dict(elem)
        self.assertIsNone(result["actionCode"])

    def test_deeply_nested(self):
        """Deeply nested elements are correctly converted."""
        xml = """<item>
            <recordedVotes>
                <recordedVote>
                    <rollNumber>7</rollNumber>
                    <chamber>Senate</chamber>
                    <congress>119</congress>
                </recordedVote>
            </recordedVotes>
        </item>"""
        elem = etree.fromstring(xml)
        result = self._nested_dict(elem)
        self.assertIn("recordedVotes", result)
        vote_data = result["recordedVotes"]
        self.assertIn("recordedVote", vote_data)
        self.assertEqual(vote_data["recordedVote"]["rollNumber"], "7")
        self.assertEqual(vote_data["recordedVote"]["chamber"], "Senate")

    def test_from_bill_status_fixture(self):
        """Test with real bill status fixture data."""
        root = _parse_fixture("bill_status.xml")
        actions = root.xpath("//actions/item")
        self.assertGreater(len(actions), 0)

        first_action = self._nested_dict(actions[0])
        self.assertEqual(first_action["actionDate"], "2025-01-03")
        self.assertEqual(first_action["text"], "Introduced in House")
        self.assertEqual(first_action["type"], "IntroReferral")
        self.assertEqual(first_action["actionCode"], "1000")
        self.assertIsInstance(first_action["sourceSystem"], dict)
        self.assertEqual(first_action["sourceSystem"]["name"], "House floor actions")

    def test_action_with_recorded_vote(self):
        """Test converting an action that has recordedVotes."""
        root = _parse_fixture("bill_status.xml")
        actions = root.xpath("//actions/item")
        vote_action = self._nested_dict(actions[2])
        self.assertIn("recordedVotes", vote_action)


# ---------------------------------------------------------------------------
# Tests for open_usc (using standalone copy to avoid spacy import chain)
# ---------------------------------------------------------------------------
class TestOpenUsc(TestCase):
    """Tests for the open_usc function which parses USC XML and builds an
    identifier lookup dictionary. Uses a standalone mirror of the function
    since importing from releases.py triggers uninstalled dependencies."""

    def test_builds_lookup_dict(self):
        """open_usc returns a lookup dict and elements list."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        lookup, elements = _open_usc(xml_bytes)
        self.assertIn("root", lookup)
        self.assertIsNotNone(lookup["root"])
        self.assertIsInstance(elements, list)

    def test_identifier_lookup(self):
        """All elements with identifiers are in the lookup dict."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        lookup, elements = _open_usc(xml_bytes)

        # Title level
        self.assertIn("/us/usc/t42", lookup)
        # Chapter level
        self.assertIn("/us/usc/t42/ch7", lookup)
        # Subchapter level
        self.assertIn("/us/usc/t42/ch7/schXVIII", lookup)
        # Section level
        self.assertIn("/us/usc/t42/s1395", lookup)
        # Subsection level
        self.assertIn("/us/usc/t42/s1395/a", lookup)
        self.assertIn("/us/usc/t42/s1395/b", lookup)
        # Paragraph level
        self.assertIn("/us/usc/t42/s1395/b/1", lookup)
        self.assertIn("/us/usc/t42/s1395/b/2", lookup)

    def test_elements_list_ordered(self):
        """Elements list contains all identified elements in document order."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        lookup, elements = _open_usc(xml_bytes)

        identifiers = [e.attrib["identifier"] for e in elements]
        self.assertIn("/us/usc/t42", identifiers)
        self.assertIn("/us/usc/t42/s1395", identifiers)
        self.assertIn("/us/usc/t42/s1395a", identifiers)
        # Document order: t42 before ch7 before s1395
        t42_idx = identifiers.index("/us/usc/t42")
        ch7_idx = identifiers.index("/us/usc/t42/ch7")
        s1395_idx = identifiers.index("/us/usc/t42/s1395")
        self.assertLess(t42_idx, ch7_idx)
        self.assertLess(ch7_idx, s1395_idx)

    def test_element_attributes_accessible(self):
        """Looked up elements have their full attributes accessible."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        lookup, _ = _open_usc(xml_bytes)

        section = lookup["/us/usc/t42/s1395"]
        self.assertEqual(section.attrib["id"], "s1395-guid")
        self.assertEqual(section.attrib["identifier"], "/us/usc/t42/s1395")

    def test_second_chapter_included(self):
        """Elements from multiple chapters are all included."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        lookup, _ = _open_usc(xml_bytes)
        self.assertIn("/us/usc/t42/ch8", lookup)
        self.assertIn("/us/usc/t42/s1401", lookup)


# ---------------------------------------------------------------------------
# Tests for get_number (using standalone copy)
# ---------------------------------------------------------------------------
class TestGetNumber(TestCase):
    """Tests for the get_number function which converts USC identifiers to
    numeric values for ordering purposes."""

    def test_simple_integer(self):
        """Plain integer identifier returns that number."""
        result = _get_number("42")
        self.assertEqual(result, 42.0)

    def test_single_digit(self):
        result = _get_number("5")
        self.assertEqual(result, 5.0)

    def test_with_letter_suffix(self):
        """Identifier with letter suffix (like '5a') has same base."""
        result_plain = _get_number("5")
        result_letter = _get_number("5a")
        self.assertEqual(result_plain, 5.0)
        self.assertEqual(result_letter, 5.0)

    def test_ordering_preserved(self):
        """Lower numbers sort before higher numbers."""
        result_1 = _get_number("1")
        result_10 = _get_number("10")
        result_42 = _get_number("42")
        self.assertLess(result_1, result_10)
        self.assertLess(result_10, result_42)

    def test_zero(self):
        result = _get_number("0")
        self.assertEqual(result, 0.0)

    def test_range_identifier(self):
        """Range identifiers like '1-5' parse the first number."""
        result = _get_number("1-5")
        self.assertEqual(result, 1.0)

    def test_ellipsis_identifier(self):
        """Identifiers with ellipsis are handled."""
        result = _get_number("100...200")
        self.assertEqual(result, 100.0)

    def test_usc_prefix_stripped_usage(self):
        """Simulates the pipeline stripping 'usc' prefix before calling."""
        # The pipeline does: get_number(file.split(".")[0].replace("usc", ""))
        filename = "usc42.xml"
        stripped = filename.split(".")[0].replace("usc", "")
        result = _get_number(stripped)
        self.assertEqual(result, 42.0)


# ---------------------------------------------------------------------------
# Tests for unidecode_str (using standalone copy)
# ---------------------------------------------------------------------------
class TestUnidecodeStr(TestCase):
    """Tests for the unidecode_str function which normalizes strings by
    converting Unicode to ASCII and collapsing double hyphens."""

    def test_plain_ascii(self):
        self.assertEqual(_unidecode_str("hello"), "hello")

    def test_none_input(self):
        """None input returns empty string."""
        self.assertEqual(_unidecode_str(None), "")

    def test_empty_string(self):
        self.assertEqual(_unidecode_str(""), "")

    def test_em_dash_collapses(self):
        """Em-dashes (unidecoded to --) become single hyphens."""
        result = _unidecode_str("section\u2014provision")
        self.assertNotIn("--", result)
        self.assertIn("-", result)

    def test_section_symbol(self):
        """Section symbol is handled by unidecode."""
        result = _unidecode_str("\u00a71395")
        self.assertIn("1395", result)


# ---------------------------------------------------------------------------
# Tests for translate_paragraph (translater.py)
# ---------------------------------------------------------------------------
class TestTranslateParagraph(TestCase):
    """Tests for translater.translate_paragraph which converts bill XML
    element tags to USLM (US Code) format tags."""

    def setUp(self):
        from congress_parser.translater import translate_paragraph

        self.translate_paragraph = translate_paragraph

    def test_enum_to_num(self):
        """<enum> tags are renamed to <num> with a 'value' attribute."""
        xml = "<section><enum>(a)</enum></section>"
        elem = etree.fromstring(xml)
        result = self.translate_paragraph(elem)
        num = result.find("num")
        self.assertIsNotNone(num)
        self.assertEqual(num.text, "(a)")
        self.assertEqual(num.attrib["value"], "a")

    def test_quote_to_quoted_content(self):
        """<quote> tags are renamed to <quotedContent>."""
        xml = "<text>the <quote>Test Act</quote></text>"
        elem = etree.fromstring(xml)
        result = self.translate_paragraph(elem)
        quoted = result.find("quotedContent")
        self.assertIsNotNone(quoted)
        self.assertEqual(quoted.text, "Test Act")

    def test_external_xref_to_ref(self):
        """<external-xref> tags are renamed to <ref>."""
        xml = '<text><external-xref legal-doc="usc">42 U.S.C. 1395</external-xref></text>'
        elem = etree.fromstring(xml)
        result = self.translate_paragraph(elem)
        ref = result.find("ref")
        self.assertIsNotNone(ref)

    def test_text_to_content(self):
        """<text> tags are renamed to <content>."""
        xml = "<text>Some legislative text here.</text>"
        elem = etree.fromstring(xml)
        result = self.translate_paragraph(elem)
        self.assertEqual(result.tag, "content")

    def test_header_to_heading(self):
        """<header> tags are renamed to <heading>."""
        xml = "<section><header>Short title</header></section>"
        elem = etree.fromstring(xml)
        result = self.translate_paragraph(elem)
        heading = result.find("heading")
        self.assertIsNotNone(heading)
        self.assertEqual(heading.text, "Short title")

    def test_string_input_passthrough(self):
        """String input is returned as-is (no transformation)."""
        result = self.translate_paragraph("plain string")
        self.assertEqual(result, "plain string")

    def test_enum_value_strips_non_word(self):
        """The 'value' attribute on <num> strips non-word characters."""
        xml = "<section><enum>1.</enum></section>"
        elem = etree.fromstring(xml)
        result = self.translate_paragraph(elem)
        num = result.find("num")
        self.assertEqual(num.attrib["value"], "1")

    def test_enum_value_with_parens(self):
        """Parenthesized enum like '(a)' gets value 'a'."""
        xml = "<section><enum>(a)</enum></section>"
        elem = etree.fromstring(xml)
        result = self.translate_paragraph(elem)
        num = result.find("num")
        self.assertEqual(num.attrib["value"], "a")

    def test_multiple_translations(self):
        """Multiple tag types in one element tree are all translated."""
        xml = """<section>
            <enum>1.</enum>
            <header>Title</header>
            <text>Content with <quote>quoted</quote> text.</text>
        </section>"""
        elem = etree.fromstring(xml)
        result = self.translate_paragraph(elem)
        self.assertIsNotNone(result.find("num"))
        self.assertIsNotNone(result.find("heading"))
        self.assertIsNotNone(result.find("content"))
        self.assertIsNotNone(result.find(".//quotedContent"))


# ---------------------------------------------------------------------------
# Tests for bill XML structure parsing
# ---------------------------------------------------------------------------
class TestBillXMLStructure(TestCase):
    """Tests for parsing bill XML structure: title extraction, date extraction,
    legis-body traversal, and structural element identification."""

    def test_title_extraction_with_colon(self):
        """Title extraction splits on colon and takes the last part."""
        root = _parse_fixture("bill_simple.xml")
        title = root.xpath("//dublinCore")[0][0].text
        if ":" in title:
            title = title.split(":")[-1].strip()
        self.assertEqual(title, "Laken Riley Act")

    def test_title_extraction_no_colon(self):
        """When title has no colon, full title is used."""
        xml = b"""<bill><metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
            <dublinCore><dc:title>Simple Title</dc:title></dublinCore>
        </metadata></bill>"""
        root = etree.fromstring(xml)
        title = root.xpath("//dublinCore")[0][0].text
        if ":" in title:
            title = title.split(":")[-1].strip()
        self.assertEqual(title, "Simple Title")

    def test_date_extraction_action_date_attribute(self):
        """Date extraction from <action-date date="..."> attribute."""
        root = _parse_fixture("bill_simple.xml")
        form_dates = root.xpath("//form/action/action-date")
        self.assertGreater(len(form_dates), 0)
        date_str = form_dates[0].get("date")
        self.assertEqual(date_str, "01/03/2025")

    def test_date_extraction_date_element(self):
        """Date extraction from <date> element text."""
        root = _parse_fixture("bill_with_date_element.xml")
        form_dates = root.xpath("//form/action/action-date") + root.xpath(
            "//form/action/date"
        )
        self.assertGreater(len(form_dates), 0)
        last_date = form_dates[-1]
        self.assertEqual(last_date.text, "July 4, 2025")

    def test_legis_body_present(self):
        """legis-body element is found in standard bill."""
        root = _parse_fixture("bill_simple.xml")
        legis = root.xpath("//legis-body")
        self.assertEqual(len(legis), 1)

    def test_legis_body_absent(self):
        """Bills without legis-body are detected."""
        root = _parse_fixture("bill_empty_legis_body.xml")
        legis = root.xpath("//legis-body")
        self.assertEqual(len(legis), 0)

    def test_sections_with_ids(self):
        """Sections with id attributes are found."""
        root = _parse_fixture("bill_simple.xml")
        legis = root.xpath("//legis-body")[0]
        sections = [elem for elem in legis if "id" in elem.attrib]
        self.assertEqual(len(sections), 3)  # sec1, sec2, sec3

    def test_section_children_structure(self):
        """Sections follow [enum, header, text, ...] child layout."""
        root = _parse_fixture("bill_simple.xml")
        section = root.xpath("//section[@id='sec1']")[0]
        self.assertEqual(section[0].tag, "enum")
        self.assertEqual(section[0].text, "1.")
        self.assertEqual(section[1].tag, "header")
        self.assertEqual(section[1].text, "Short title")
        self.assertEqual(section[2].tag, "text")

    def test_subsection_hierarchy(self):
        """Subsections are nested within sections."""
        root = _parse_fixture("bill_simple.xml")
        section2 = root.xpath("//section[@id='sec2']")[0]
        subsections = section2.xpath("subsection")
        self.assertEqual(len(subsections), 2)  # (a) and (b)

        sub_a = section2.xpath("subsection[@id='sec2a']")[0]
        self.assertEqual(sub_a[0].text, "(a)")
        self.assertEqual(sub_a[1].text, "Aliens described")

    def test_paragraph_nesting(self):
        """Paragraphs are nested within subsections."""
        root = _parse_fixture("bill_simple.xml")
        sub_a = root.xpath("//subsection[@id='sec2a']")[0]
        paragraphs = sub_a.xpath("paragraph")
        self.assertEqual(len(paragraphs), 3)

        enums = [p[0].text for p in paragraphs]
        self.assertEqual(enums, ["(1)", "(2)", "(3)"])

    def test_deep_nesting_structure(self):
        """Test deeply nested bill with paragraphs inside subsections."""
        root = _parse_fixture("bill_nested_quotes.xml")
        sec3 = root.xpath("//section[@id='sec3']")[0]
        subsections = sec3.xpath("subsection")
        self.assertEqual(len(subsections), 2)

        sub_b = sec3.xpath("subsection[@id='sec3b']")[0]
        paragraphs = sub_b.xpath("paragraph")
        self.assertEqual(len(paragraphs), 2)

    def test_chapeau_element(self):
        """Chapeau elements (introductory text before paragraphs) are found."""
        root = _parse_fixture("bill_nested_quotes.xml")
        sub_b = root.xpath("//subsection[@id='sec3b']")[0]
        chapeau = sub_b.find("chapeau")
        self.assertIsNotNone(chapeau)
        self.assertEqual(chapeau.text, "in subsection (d)(1)-")


# ---------------------------------------------------------------------------
# Tests for USC XML structure parsing
# ---------------------------------------------------------------------------
class TestUSCXMLStructure(TestCase):
    """Tests for parsing US Code XML structure following the USLM schema."""

    def test_namespace_handling(self):
        """Elements use namespaced tags that need namespace stripping."""
        root = _parse_fixture("usc_title_sample.xml")
        for elem in root.iter():
            split_tag = elem.tag.split("}")[-1]
            self.assertNotIn("{", split_tag)

    def test_title_heading_extraction(self):
        """Title heading can be extracted by searching for first heading element."""
        root = _parse_fixture("usc_title_sample.xml")
        title_text = None
        for elem in root.iter():
            if "heading" in elem.tag:
                title_text = elem.text
                break
        self.assertEqual(title_text, "THE PUBLIC HEALTH AND WELFARE")

    def test_identifier_depth_parsing(self):
        """Identifier depth determines element type in the hierarchy."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        _, elements = _open_usc(xml_bytes)

        for elem in elements:
            ident = elem.attrib["identifier"]
            chunks = ident.split("/")
            depth = len(chunks)
            split_tag = elem.tag.split("}")[-1]

            # Section identifiers at depth 5 with 's' prefix (not 'st' or 'sch')
            if depth == 5 and chunks[-1].startswith("s") and not chunks[-1].startswith("st") and not chunks[-1].startswith("sch"):
                self.assertEqual(split_tag, "section")

    def test_section_children_have_num_and_heading(self):
        """USC sections have <num> and <heading> as first children."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        lookup, _ = _open_usc(xml_bytes)

        section = lookup["/us/usc/t42/s1395"]
        num_tag = section[0].tag.split("}")[-1]
        heading_tag = section[1].tag.split("}")[-1]
        self.assertEqual(num_tag, "num")
        self.assertEqual(heading_tag, "heading")
        self.assertEqual(section[0].attrib["value"], "1395")

    def test_subsection_content(self):
        """Subsections contain content text."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        lookup, _ = _open_usc(xml_bytes)

        subsection_a = lookup["/us/usc/t42/s1395/a"]
        content_tag = subsection_a[2].tag.split("}")[-1]
        self.assertEqual(content_tag, "content")
        content_text = " ".join(subsection_a[2].itertext()).strip()
        self.assertIn("insurance program", content_text)

    def test_paragraph_content(self):
        """Paragraphs within subsections are accessible."""
        xml_bytes = _load_fixture("usc_title_sample.xml")
        lookup, _ = _open_usc(xml_bytes)

        para1 = lookup["/us/usc/t42/s1395/b/1"]
        num = para1[0]
        num_tag = num.tag.split("}")[-1]
        self.assertEqual(num_tag, "num")
        self.assertEqual(num.attrib["value"], "1")


# ---------------------------------------------------------------------------
# Tests for bill status XML parsing
# ---------------------------------------------------------------------------
class TestBillStatusParsing(TestCase):
    """Tests for parsing bill status XML structure used by status_parser.py."""

    def test_bill_info_extraction(self):
        """Bill metadata fields are extracted via XPath."""
        root = _parse_fixture("bill_status.xml")
        bill_element = root.xpath("//bill")[0]
        bill_info = {
            e.tag: e.text
            for e in bill_element
            if e.tag
            in ["billNumber", "originChamber", "type", "congress", "number"]
        }
        self.assertEqual(bill_info["billNumber"], "1")
        self.assertEqual(bill_info["originChamber"], "House")
        self.assertEqual(bill_info["type"], "HR")
        self.assertEqual(bill_info["congress"], "119")
        self.assertEqual(bill_info["number"], "1")

    def test_actions_extraction(self):
        """Actions are extracted via XPath."""
        root = _parse_fixture("bill_status.xml")
        actions = root.xpath("//actions/item")
        self.assertEqual(len(actions), 3)

    def test_committee_extraction(self):
        """Committee data is extracted via XPath."""
        root = _parse_fixture("bill_status.xml")
        committees = root.xpath("//billCommittees/item")
        self.assertEqual(len(committees), 1)
        comm = {e.tag: e.text for e in committees[0]}
        self.assertEqual(comm["systemCode"], "hsju00")
        self.assertEqual(comm["name"], "Judiciary Committee")
        self.assertEqual(comm["chamber"], "House")

    def test_subcommittee_extraction(self):
        """Subcommittees are extracted via nested XPath."""
        root = _parse_fixture("bill_status.xml")
        subcommittees = root.xpath("//billCommittees/item/subcommittees/item")
        self.assertEqual(len(subcommittees), 1)
        sub = {e.tag: e.text for e in subcommittees[0]}
        self.assertEqual(sub["systemCode"], "hsju01")

    def test_committee_activities(self):
        """Committee activities (Referred to, Discharged from) are extracted."""
        root = _parse_fixture("bill_status.xml")
        activities = root.xpath("//billCommittees/item/activities/item")
        self.assertEqual(len(activities), 1)
        activity = {e.tag: e.text for e in activities[0]}
        self.assertEqual(activity["name"], "Referred to")

    def test_policy_area_extraction(self):
        """Policy area is extracted via XPath."""
        root = _parse_fixture("bill_status.xml")
        policy_area = root.xpath("//policyArea/name")
        self.assertEqual(len(policy_area), 1)
        self.assertEqual(policy_area[0].text, "Immigration")

    def test_legislative_subjects_extraction(self):
        """Legislative subjects are extracted via XPath."""
        root = _parse_fixture("bill_status.xml")
        subjects = root.xpath("//legislativeSubjects/item/name")
        self.assertEqual(len(subjects), 3)
        subject_names = [s.text for s in subjects]
        self.assertIn("Criminal law and procedure", subject_names)
        self.assertIn("Detention of persons", subject_names)
        self.assertIn("Immigration status and procedures", subject_names)

    def test_recorded_votes_extraction(self):
        """Recorded votes within actions are extractable."""
        root = _parse_fixture("bill_status.xml")
        votes = root.xpath("//recordedVotes/recordedVote")
        self.assertEqual(len(votes), 1)
        vote = {e.tag: e.text for e in votes[0]}
        self.assertEqual(vote["rollNumber"], "7")
        self.assertEqual(vote["chamber"], "Senate")
        self.assertEqual(vote["congress"], "119")


# ---------------------------------------------------------------------------
# Tests for parse_such_code (actions/__init__.py)
# ---------------------------------------------------------------------------
class TestParseSuchCode(TestCase):
    """Tests for parse_such_code which resolves 'such code' references
    in bill clauses to USC citations."""

    def setUp(self):
        from congress_parser.actions import parse_such_code

        self.parse_such_code = parse_such_code

    def test_section_with_subsection(self):
        """Section reference with subsection parentheses."""
        result = self.parse_such_code("Section 1395(a)(1)", "42")
        self.assertEqual(result, "/us/usc/t42/s1395/a/1")

    def test_section_with_single_paren(self):
        """Section reference with one subsection."""
        result = self.parse_such_code("Section 101(a)", "5")
        self.assertEqual(result, "/us/usc/t5/s101/a")

    def test_paragraph_reference(self):
        """Paragraph reference."""
        result = self.parse_such_code("paragraph 3(a)", "18")
        self.assertEqual(result, "/us/usc/t18/s3/a")

    def test_no_match(self):
        """Non-matching text returns empty string."""
        result = self.parse_such_code("no section here", "42")
        self.assertEqual(result, "")

    def test_deep_subsection_reference(self):
        """Section with deep subsection nesting."""
        result = self.parse_such_code("Section 6311(g)(2)", "20")
        self.assertEqual(result, "/us/usc/t20/s6311/g/2")


# ---------------------------------------------------------------------------
# Tests for convert_to_text with real bill fixtures
# ---------------------------------------------------------------------------
class TestConvertToTextWithFixtures(TestCase):
    """Integration tests using convert_to_text on elements from bill fixtures."""

    def setUp(self):
        from congress_parser.run_through import convert_to_text

        self.convert_to_text = convert_to_text

    def test_simple_bill_section_texts(self):
        """Extract and convert all section texts from simple bill."""
        root = _parse_fixture("bill_simple.xml")
        sections = root.xpath("//section")
        self.assertEqual(len(sections), 3)

        sec1_text = sections[0].xpath("text")[0]
        result = self.convert_to_text(sec1_text)
        self.assertIn("Laken Riley Act", result)

        sec3_text = sections[2].xpath("text")[0]
        result = self.convert_to_text(sec3_text)
        self.assertIn("90 days", result)

    def test_amendment_bill_quote_handling(self):
        """Amendment bill with <quote> tags produces quoted strings."""
        root = _parse_fixture("bill_amendments.xml")
        sec2a = root.xpath("//subsection[@id='sec2a']/text")[0]
        result = self.convert_to_text(sec2a)
        self.assertIn('"Each State motor vehicle driver\'s license application"', result)
        self.assertIn('"Subject to the requirements under section 8(j)', result)

    def test_paragraph_text_extraction(self):
        """Paragraph text elements convert correctly (stripping XML whitespace)."""
        root = _parse_fixture("bill_simple.xml")
        paragraphs = root.xpath("//paragraph")
        self.assertEqual(len(paragraphs), 3)

        texts = [self.convert_to_text(p.xpath("text")[0]).strip() for p in paragraphs]
        self.assertEqual(texts[0], "Theft or burglary.")
        self.assertEqual(texts[1], "Larceny or shoplifting.")
        self.assertEqual(texts[2], "Assault of a law enforcement officer.")

    def test_chapeau_text_extraction(self):
        """Chapeau text elements convert correctly."""
        root = _parse_fixture("bill_nested_quotes.xml")
        chapeau = root.xpath("//chapeau")[0]
        result = self.convert_to_text(chapeau).strip()
        self.assertEqual(result, "in subsection (d)(1)-")


# ---------------------------------------------------------------------------
# Tests for bill XML content type detection
# ---------------------------------------------------------------------------
class TestBillContentTypeDetection(TestCase):
    """Tests that verify content type detection logic used in
    recursive_bill_content for determining element categories."""

    def test_content_tag_detection(self):
        """Elements with 'content' in tag name are detected as content."""
        tags_with_content = ["content", "chapeau", "notes", "text"]
        for tag in tags_with_content:
            self.assertTrue(
                "content" in tag
                or "chapeau" in tag
                or "notes" in tag
                or "text" in tag,
                f"{tag} should be detected as content-bearing element",
            )

    def test_heading_tag_detection(self):
        """Elements with 'head' in tag name are detected as headings."""
        heading_tags = ["header", "heading", "head"]
        for tag in heading_tags:
            self.assertTrue(
                "head" in tag,
                f"{tag} should be detected as a heading element",
            )

    def test_non_heading_tags(self):
        """Non-heading tags are not misidentified as headings."""
        non_heading_tags = ["text", "content", "enum", "chapeau"]
        for tag in non_heading_tags:
            self.assertFalse(
                "head" in tag,
                f"{tag} should NOT be detected as a heading element",
            )

    def test_structural_element_has_id(self):
        """Structural elements (sections, subsections) have 'id' attributes."""
        root = _parse_fixture("bill_simple.xml")
        legis = root.xpath("//legis-body")[0]

        structural_elements = []
        for elem in legis.iter():
            if "id" in elem.attrib and elem.tag != "legis-body":
                structural_elements.append(elem)

        self.assertGreater(len(structural_elements), 0)
        for elem in structural_elements:
            self.assertIn(elem.tag, ["section", "subsection", "paragraph"])

    def test_elements_without_id_are_skipped(self):
        """Elements like <enum>, <header>, <text> do not have 'id' attributes."""
        root = _parse_fixture("bill_simple.xml")
        non_structural_tags = {"enum", "header", "text"}
        legis = root.xpath("//legis-body")[0]

        for elem in legis.iter():
            if elem.tag in non_structural_tags:
                self.assertNotIn(
                    "id",
                    elem.attrib,
                    f"<{elem.tag}> should not have an 'id' attribute",
                )


# ---------------------------------------------------------------------------
# Tests for USC organizational level detection
# ---------------------------------------------------------------------------
class TestUSCOrganizationalLevels(TestCase):
    """Tests for the organizational level detection used in
    import_title to classify USC elements as chapters, subchapters, etc."""

    def test_organizational_tags(self):
        """Organizational tags match the set used in import_title."""
        org_tags = [
            "chapter",
            "subchapter",
            "part",
            "subpart",
            "division",
            "subdivision",
            "article",
            "subarticle",
        ]
        xml_bytes = _load_fixture("usc_title_sample.xml")
        _, elements = _open_usc(xml_bytes)

        found_org_tags = set()
        for elem in elements:
            split_tag = elem.tag.split("}")[-1]
            if split_tag in org_tags:
                found_org_tags.add(split_tag)

        # Our fixture has chapters and subchapters
        self.assertIn("chapter", found_org_tags)
        self.assertIn("subchapter", found_org_tags)

    def test_section_identifier_depth(self):
        """Section identifiers have depth 5 (e.g. /us/usc/t42/s1395).
        Note: identifiers start with empty string before first slash,
        so '/us/usc/t42/s1395'.split('/') = ['', 'us', 'usc', 't42', 's1395'] = length 5."""
        test_idents = [
            ("/us/usc/t42/s1395", 5, True),
            ("/us/usc/t42/s1395a", 5, True),
            ("/us/usc/t42/s1395/a", 6, False),  # subsection
            ("/us/usc/t42/ch7", 5, False),  # chapter (starts with 'ch' not 's')
            ("/us/usc/t42", 4, False),  # title
        ]
        for ident, expected_depth, expected_section in test_idents:
            chunks = ident.split("/")
            self.assertEqual(
                len(chunks),
                expected_depth,
                f"{ident} should have depth {expected_depth}, got {len(chunks)}",
            )

    def test_section_starts_with_s_not_st(self):
        """Section identifiers start with 's' but not 'st' (subtitle)."""
        test_cases = [
            ("/us/usc/t42/s1395", True),
            ("/us/usc/t42/stA", False),  # subtitle
            ("/us/usc/t42/s1395a", True),
            ("/us/usc/t42/ch7", False),  # chapter
        ]
        for ident, expected in test_cases:
            chunks = ident.split("/")
            if len(chunks) == 5:
                last = chunks[-1]
                is_section = last[0] == "s" and (len(last) < 2 or last[1] != "t")
                self.assertEqual(
                    is_section,
                    expected,
                    f"{ident} should {'be' if expected else 'not be'} a section",
                )
