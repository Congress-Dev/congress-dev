from typing import Optional, TypedDict, Any
import re
import logging

from unidecode import unidecode

cite_contexts = {"last_title": None}

SEC_TITLE_REGEX = re.compile(
    r"(?:(?:Subsection|paragraph) \((?P<finalsub>.?)\) of )?Section (?P<section>\d*)(?:\((?P<sub1>.*?)\)(?:\((?P<sub2>.*?)\)(?:\((?P<sub3>.*?)\))?)?)? of title (?P<title>[0-9A]*)",
    re.IGNORECASE,
)

SUB_SEC_REGEX = re.compile(r"subsection\s\((.)\)", re.IGNORECASE)

SUCH_TITLE_REGEX = re.compile(
    r"Section (?P<section>\d*)(?:\((?P<sub1>.*?)\)(?:\((?P<sub2>.*?)\)(?:\((?P<sub3>.*?)\))?)?)? of such (title|act)",
    re.IGNORECASE,
)

USC_CITE_REGEX = re.compile(
    r"\(?(?P<title>\d+?) U\.S\.C\. (?P<section>.*)\)?",
    re.IGNORECASE,
)
SUB_OF_REGEX = re.compile(r"sub(?:section)?\s\((.)\)", re.IGNORECASE)


def find_extra_clause_references(snippet):
    """
    Capture outside references like "Clause (i)" -> returns ["i"].
    This example looks for 'clause|subclause|paragraph|subparagraph|part|item'.
    Add more if needed.
    """
    pattern = r"(?:clause|subclause|paragraph|subparagraph|part|item)\s*\(([^)]+)\)"
    matches = re.findall(pattern, snippet, flags=re.IGNORECASE)
    return matches


def extract_usc_cite(text: str) -> Optional[str]:
    regex_match = USC_CITE_REGEX.search(text)
    if regex_match:
        # We found a USC cite
        #  - (22 U.S.C. 2671(b)(2)(A)(ii))
        #  - (52 U.S.C. 20504)
        cite = "/us/usc/t{}".format(regex_match["title"])
        cite += "/s{}".format(regex_match["section"].split("(")[0])
        if "(" in regex_match["section"]:
            possibles = [
                x.replace(")", "")
                for x in regex_match["section"].split("(", 1)[1].split(")(")
            ]
            if len(possibles) > 0:
                cite += "/" + "/".join(possibles)
        return cite
    return None

class ActionObject(TypedDict):
    parent: str
    enum: str
    text: str
    text_element: Any
    amended: bool
    next: str


def parse_action_for_cite(action_object: ActionObject, parent_cite: str = "") -> str:
    """
    Looks at a given action object to determine what citation it is trying to edit.
    A citation represents a location in the USCode

    # TODO: Split function apart

    Args:
        action_object (dict): An object represented an extract action

    Returns:
        str: A USCode citation str
    """
    # print(action_object)
    try:
        cite = None
        if action_object["text_element"] is not None:
            # print(
            #     etree.tostring(
            #         action_object["text_element"], pretty_print=True, encoding="unicode"
            #     )
            # )
            xref = action_object["text_element"].find("external-xref[@legal-doc='usc']")
            if not isinstance(action_object["text_element"].text, str):
                return ""
            if xref is not None:
                cite_text = unidecode(xref.attrib["parsable-cite"])
            else:
                cite_text = None
            elem_text = unidecode(action_object["text_element"].text)
            if cite_text:
                cite = extract_usc_cite(xref.text)
            else:
                cite = extract_usc_cite(elem_text)

            # If we have a full cite, lets just check for "Clause (i) of" type references
            extra_cite = find_extra_clause_references(elem_text)
            if len(extra_cite) > 0:
                if cite:
                    cite += "/" + "/".join(extra_cite)
                    return cite

            # Assume that the usc_cite has the full path
            # Otherwise we may need to parse the of such title stuff

            regex_match = SUCH_TITLE_REGEX.search(elem_text)
            if regex_match:
                if parent_cite:
                    # This is a bit wrong, parent_cite will currently already have a section
                    # But I need to do something earlier in the parser to enable a better solution
                    cite = "/".join(parent_cite.split("/")[:5]) + "/" + regex_match["section"]
                else:
                    cite = "/us/usc/t{}/s{}".format(
                        cite_contexts["last_title"], regex_match["section"]
                    )
                possibles = [
                    regex_match[f"sub{x}"]
                    for x in range(1, 3)
                    if regex_match[f"sub{x}"]
                ]
                if len(possibles) > 0:
                    cite += "/" + "/".join(possibles)
                cite_contexts[action_object["enum"]] = cite
                return cite
            if action_object["parent"] in cite_contexts:
                parent_cite = cite_contexts[action_object["parent"]]
            else:
                parent_cite = ""
            regex_match = SUB_SEC_REGEX.search(elem_text)
            if regex_match:
                cite = parent_cite + "/" + regex_match[1]
                cite_contexts[action_object["enum"]] = cite
                cite_split = cite.split("/")
                if len(cite_split) > 3:
                    cite_contexts["last_title"] = cite_split[3][1:]
                return cite
            if cite:
                return cite
    except Exception as e:
        logging.error("Uncaught exception", exc_info=e)

    return parent_cite
