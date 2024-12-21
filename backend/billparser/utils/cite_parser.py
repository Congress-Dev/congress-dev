from billparser.helpers import convert_to_usc_id
import re
import logging
from lxml import etree
cite_contexts = {"last_title": None}

SecTitleRegex = re.compile(
    r"(?:(?:Subsection|paragraph) \((?P<finalsub>.?)\) of )?Section (?P<section>\d*)(?:\((?P<sub1>.*?)\)(?:\((?P<sub2>.*?)\)(?:\((?P<sub3>.*?)\))?)?)? of title (?P<title>[0-9A]*)",
    re.IGNORECASE,
)

SubSecRegex = re.compile(r"subsection\s\((.)\)", re.IGNORECASE)

SuchTitleRegex = re.compile(
    r"Section (?P<section>\d*)(?:\((?P<sub1>.*?)\)(?:\((?P<sub2>.*?)\)(?:\((?P<sub3>.*?)\))?)?)? of such (title)",
    re.IGNORECASE,
)


def parse_action_for_cite(action_object: dict) -> str:
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
        parent_cite = ""
        if action_object["text_element"] is not None:
            # print(
            #     etree.tostring(
            #         action_object["text_element"], pretty_print=True, encoding="unicode"
            #     )
            # )
            xref = action_object["text_element"].find("external-xref[@legal-doc='usc']")
            if xref is not None:
                cite = convert_to_usc_id(xref)
                action_object["cite_parse"] = str(cite)
                cite_contexts[action_object["enum"]] = str(cite)
                if len(cite.split("/")) > 3:
                    cite_contexts["last_title"] = cite.split("/")[3][1:]
                return cite
            if not isinstance(action_object["text_element"].text, str):
                return ""
            text_obj = action_object["text_element"].text.strip()
            SecTitleRegex_match = SecTitleRegex.search(text_obj)
            if SecTitleRegex_match:
                cite = "/us/usc/t{}/s{}".format(
                    SecTitleRegex_match["title"], SecTitleRegex_match["section"]
                )
                possibles = [
                    SecTitleRegex_match[f"sub{x}"]
                    for x in range(1, 3)
                    if SecTitleRegex_match[f"sub{x}"]
                ]
                if SecTitleRegex_match["finalsub"]:
                    possibles.append(SecTitleRegex_match["finalsub"])
                if len(possibles) > 0:
                    cite += "/" + "/".join(possibles)
                cite_contexts[action_object["enum"]] = cite
                cite_split = cite.split("/")
                if len(cite_split) > 3:
                    cite_contexts["last_title"] = cite.split("/")[3][1:]
                return cite
            SuchTitleRegex_match = SuchTitleRegex.search(text_obj)
            if SuchTitleRegex_match:
                cite = "/us/usc/t{}/s{}".format(
                    cite_contexts["last_title"], SuchTitleRegex_match["section"]
                )
                possibles = [
                    SuchTitleRegex_match[f"sub{x}"]
                    for x in range(1, 3)
                    if SuchTitleRegex_match[f"sub{x}"]
                ]
                if len(possibles) > 0:
                    cite += "/" + "/".join(possibles)
                cite_contexts[action_object["enum"]] = cite
                return cite
            if action_object["parent"] in cite_contexts:
                parent_cite = cite_contexts[action_object["parent"]]
            else:
                parent_cite = ""
            SubSecRegex_match = SubSecRegex.search(text_obj)
            if SubSecRegex_match:
                cite = parent_cite + "/" + SubSecRegex_match[1]
                cite_contexts[action_object["enum"]] = cite
                cite_split = cite.split("/")
                if len(cite_split) > 3:
                    cite_contexts["last_title"] = cite_split[3][1:]
                return cite
    except Exception as e:
        logging.error("Uncaught exception", exc_info=e)

    return parent_cite
