from typing import Dict, List, Optional, TypedDict, Any
import re
import logging

from congress_parser.actions import Action, ActionType
from unidecode import unidecode

cite_contexts = {"last_title": None}

SEC_TITLE_REGEX = re.compile(
    r"(?:(?:Subsection|paragraph) \((?P<finalsub>.*?)\) of )?Section (?P<section>.*?) of title (?P<title>[0-9Aa]*), United States Code",
    re.IGNORECASE,
)
TITLE_SEC_REGEX = re.compile(
    r"title (?P<title>[0-9Aa]*), United States Code, .*?section (?P<section>.*?)\s",
    re.IGNORECASE,
)

SUB_SEC_REGEX = re.compile(
    r"(?:section|subsection|paragraph|clause)\s(\d?(?:\([^()]*\))+)", re.IGNORECASE
)

SUCH_TITLE_REGEX = re.compile(
    r"Section (?P<section>\d*)(?:\((?P<sub1>.*?)\)(?:\((?P<sub2>.*?)\)(?:\((?P<sub3>.*?)\))?)?)? of such (title|act)",
    re.IGNORECASE,
)

USC_CITE_REGEX = re.compile(
    r"\((?P<title>\d+?[aA]?) U\.S\.C\. (?P<section>.*?)\)(?:\s|,|\.)",
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


def split_section_text(text: str) -> List[str]:
    # Takes strings like "b)(2)(A)(ii)" and returns ["b", "2", "A", "ii"]
    return [x.replace(")", "") for x in text.split(")(")]


def extract_usc_cite(text: str) -> Optional[str]:
    regex_match = USC_CITE_REGEX.search(text)
    if regex_match:
        # We found a USC cite
        #  - (22 U.S.C. 2671(b)(2)(A)(ii))
        #  - (52 U.S.C. 20504)
        def leading_zeros(inp: str) -> str:
            first_digit = inp[0]
            if first_digit.isdigit() and (len(inp) == 1 or not inp[-1].isdigit()):
                return "0" + inp
            return inp

        cite = "/us/usc/t{}".format(regex_match["title"])

        cite += "/s{}".format(
            regex_match["section"].replace("note", "").strip().split("(")[0]
        )
        if "(" in regex_match["section"]:
            possibles = split_section_text(regex_match["section"].split("(", 1)[1])

            if len(possibles) > 0:
                cite += "/" + "/".join(possibles)
        if "note" in regex_match["section"]:
            cite += "/note"
        return cite
    return None


class ActionObject(TypedDict):
    parent: str
    enum: str
    text: str
    text_element: Any
    amended: bool
    next: str


class CiteObject(TypedDict):
    text: str
    cite: str

    # If we believe the cite is entirely resolved
    # /usc/t42/s18071 <- Fully resolved to a section
    # /s18071 <- Partially resolved to a section
    # /usc/t42 <- Fully resolved to a title
    # /s18071/a <- Partially resolved to a subsection
    # /a/1 <- Partially resolved to a subsubsection
    # It's the expectation that whomever is consuming this data will be able to handle
    # the partial resolution via combining it with the parent(s)
    complete: bool = False


def parse_text_for_cite(
    text: str, action_dict: Dict[ActionType, Action] = None
) -> List[CiteObject]:
    action_dict = action_dict or {}
    cites_found: List[CiteObject] = []
    cite = extract_usc_cite(text)
    if cite:
        print(cite)
        # If we have a full cite, lets just check for "Clause (i) of" type references
        extra_cite = find_extra_clause_references(text)
        if len(extra_cite) > 0:
            cite += "/" + "/".join(extra_cite)
            cites_found.append({"text": text, "cite": cite, "complete": True})
            return cites_found
        else:
            cites_found.append({"text": text, "cite": cite, "complete": True})
            return cites_found
    regex_match = SEC_TITLE_REGEX.search(text) or TITLE_SEC_REGEX.search(text)
    print(regex_match)
    if regex_match:
        cite = "/us/usc/t{}/s{}".format(
            regex_match["title"], regex_match["section"].split("(")[0]
        )

        # Parse the subsections
        if "(" in regex_match["section"]:
            possibles = split_section_text(regex_match["section"].split("(", 1)[1])
            if len(possibles) > 0:
                cite += "/" + "/".join(possibles)

        # Maybe there was an additional subclause
        if regex_match.groupdict().get("finalsub"):
            possibles = split_section_text(regex_match["finalsub"].split("(", 1)[0])
            if len(possibles) > 0:
                cite += "/" + "/".join(possibles)
        cites_found.append(
            {
                "text": text,
                "cite": cite,
                "complete": True,
            }
        )
        print(cites_found)
    else:
        regex_match = SUCH_TITLE_REGEX.search(text)
        if regex_match:
            cites_found.append(
                {
                    "text": text,
                    "cite": "/s{}".format(regex_match["section"]),
                    "complete": False,
                }
            )
        else:
            regex_match = SUB_SEC_REGEX.search(text)
            if regex_match:
                # We are splitting and replacing here to handle cases like
                # subsection (a)(1)
                # We split on )( so we can get between all the letters, then we remove the edge parens, and put / between them all
                cites_found.append(
                    {
                        "text": text,
                        "cite": "/"
                        + "/".join(
                            [
                                x.replace("(", "").replace(")", "")
                                for x in regex_match[1].split(")(")
                            ]
                        ),
                        "complete": False,
                    }
                )

    return cites_found


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
            print(f"{extra_cite=}")
            print(f"{cite=}")
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
                    cite = (
                        "/".join(parent_cite.split("/")[:5])
                        + "/"
                        + regex_match["section"]
                    )
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
