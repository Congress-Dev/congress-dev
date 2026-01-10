from typing import Optional
from lxml import etree
import re
from congress_parser.translater import translate_paragraph

from unidecode import unidecode

# TODO: I think this is mostly unused

cite_regex = re.compile(r"^(\d+) [USC\.]+ (.*?)(\(.+\))?$", re.IGNORECASE)
section_regex = re.compile(r"^Section (.*?)(\(.*?\))?$", re.IGNORECASE)
part_regex = re.compile(r"\((.*?)\)", re.IGNORECASE)

USC_CITE_REGEX = re.compile(
    r"\(?(?P<title>\d+?) U\.S\.C\. (?P<section>.*)\)?",
    re.IGNORECASE,
)

def _parse_usc_cite(cite_txt: str) -> Optional[str]:
    cite_match = USC_CITE_REGEX.search(cite_txt)
    if cite_match:
        # We found a USC cite
        #  - (22 U.S.C. 2671(b)(2)(A)(ii))
        #  - (52 U.S.C. 20504)
        cite = "/us/usc/t{}".format(cite_match["title"])
        cite += "/s{}".format(cite_match["section"].split("(")[0])
        if "(" in cite_match["section"]:
            possibles = [
                x.replace(")", "")
                for x in cite_match["section"].split("(", 1)[1].split(")(")
            ]
            if len(possibles) > 0:
                cite += "/" + "/".join(possibles)
        return cite
    return None

# /us/usc/t7/s7333/e
def convert_to_usc_id(xref):
    """
    # TODO: This is complicated

    Args:
        xref ([type]): [description]

    Returns:
        [type]: [description]
    """
    try:
        # doc = xref.attrib['legal-doc']
        cite = unidecode(xref.attrib["parsable-cite"])
        xref.text = unidecode(xref.text)
        section_match = section_regex.match(xref.text)
        cite_match = _parse_usc_cite(xref.text)
        if cite_match:
            return cite_match
        elif section_match:
            groups = section_match.groups()
            if groups[-1] is not None:
                parts = part_regex.findall(groups[-1])
            else:
                parts = []
            cite_split = cite.split("/")
            if cite_split[-1] == groups[0]:
                if cite_split[0] == "usc":
                    return "/us/usc/t{}/s{}/{}".format(
                        cite_split[1], cite_split[2], "/".join(parts)
                    )

    except Exception as e:
        # print(e)
        pass
    return ""


def determine_action(xref):
    # TODO: Unused function?
    par = xref.getparent()
    texts = [x for x in par.itertext() if x != xref.text]
    # print("actions", texts[-1])
    if "adding at the end the following" in texts[-1]:
        return "APPEND"
    if "is amended—" in texts[-1]:
        return "AMEND"
    return None


def look_for_directions(text):
    # TODO: Unused function?
    if "by striking" in text:
        overall = "striking"
    print("Directions", text)
    tokens = text.split(" ")
    if "paragraph" in tokens:
        print("Found paragraph descriptor")
        paragraph_id = tokens[tokens.index("paragraph") + 1]
        return
        print(paragraph_id)
    print(tokens)


def determine_result(paragraph):
    # TODO: Unused function
    print("dtrs")
    text = [x.strip() for x in paragraph.itertext() if x.strip() != ""]
    print(text[0])
    look_for_directions(text[1])


records = []
usc_root = None
usc_29 = {}


def parse_usc(title):
    # TODO: Unused function?
    global usc_root, usc_29
    with open("usc/usc{}.xml".format(title), "rb") as file:
        usc_root = etree.fromstring(file.read())
        ids = usc_root.xpath("//*[@identifier]")
        for id in ids:
            usc_29[id.attrib["identifier"]] = id


def parse(file, name):
    # TODO: Unused function?
    global usc_root, usc_29
    ref_boi = []
    try:
        root = etree.fromstring(file.read().decode())
        sections = root.xpath("//section")
        for section in sections:
            refs = section.findall(".//external-xref")
            for ref in refs:
                section_cite = convert_to_usc_id(ref)
                ref_boi += [
                    {
                        "name": name,
                        "ref": " ".join([x.strip() for x in ref.itertext()]),
                        "parse": section_cite,
                        "text": " ".join(
                            [x.strip() for x in ref.getparent().itertext()]
                        ),
                        "attrib": ref.attrib,
                    }
                ]
                print("Sec", section_cite)
                action = determine_action(ref)
                print("Action", action)
                paragraphs = section.findall("paragraph")
                for paragraph in paragraphs:

                    print(paragraph.getchildren()[0].text)
                    determine_result(paragraph)
                print(section_cite)

            print(section.text)

        for para in root.xpath("//paragraph"):
            print(etree.tostring(para, pretty_print=True).decode())
            print(etree.tostring(translate_paragraph(para), pretty_print=True).decode())
    except:
        return []

    return ref_boi


def prepare(x):
    return {**x, "child": []}


def treeify(bill_contents):
    lookup = {x.get("bill_content_id"): prepare(x) for x in bill_contents}
    lookup["Legis"] = {"child": []}
    del bill_contents
    for bill in lookup:
        cur = lookup[bill]
        par = cur.get("parent", "Legis")
        if cur.get("bill_content_id") is not None:
            lookup[par]["child"].append(cur)
    for bill in lookup:
        lookup[bill]["child"] = sorted(
            lookup[bill]["child"], key=lambda x: x.get("order", 0)
        )
    return lookup["Legis"]


# parse_usc('29')

# for i in range(7000,7100):
#     try:
#         with open('bills/hr{}.xml'.format(i), 'rb') as f:
#             records += parse(f, 'hr{}'.format(i))
#     except:
#         pass
# with open('bills/hr7030.xml', 'rb') as f:
#     records = parse(f, 'hr7030')

# # tree = etree.ElementTree(usc_root)
# # tree.write("output.xml")
# df = pandas.DataFrame.from_records(records)
# df.to_csv('out.csv')
