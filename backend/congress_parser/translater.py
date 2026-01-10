import re

translate = {"enum": "num"}


def translate_paragraph(element):
    """
    Transforms an XML element from the USCode version into HTML
    """
    if isinstance(element, str):
        return element

    for elem in element.iter():
        if elem.tag == "enum":
            elem.tag = "num"
            elem.attrib["value"] = re.sub("\W+", "", elem.text)
        if elem.tag == "quote":
            elem.tag = "quotedContent"
        if elem.tag == "external-xref":
            elem.tag = "ref"
        if elem.tag == "text":
            elem.tag = "content"
        if elem.tag == "header":
            elem.tag = "heading"
    return element
