import re
from billparser.logger import log


regex_holder = {
    "SHORT-TITLE": [
        r"This (?P<context_type>(?:act|(?:sub)?title)) may be cited as the (?P<title>.+?)\."
    ],
    "PURPOSE": [r"The purpose of this Act is (?P<purpose>.+)\."],
    "CONGRESS-FINDS": [r"Congress finds the following:"],
    "REPLACE-SECTION": [
        r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is (?:further )?amended.?to read as follows:?",
        r"The (?P<target>.+?) is amended to read as follows:",
        r"by amending (?P<target>.+?) to read as follows:",
    ],
    "IN-CONTEXT": [r"^in (?P<target>.*)-$"],
    "AMEND-MULTIPLE": [
        r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is (?:further )?amended.?",
        r"(?P<target>.+?) of Public Law (?P<public_law_cite>.+?) \((?P<within>.+?)\) is amended-?",
    ],
    "STRIKE-TEXT": [
        r"(?:(?P<target>.+?) of (?P<within>.+?) is amended )?by striking \"(?P<to_remove_text>.+?)\" and inserting \"(?P<to_replace>.+?)\"\.",
        r"(?:in (?P<target>.*),)?by striking \"(?P<to_remove_text>.+?)\" and inserting \"(?P<to_replace>.+?)\"(?:\.|;)",
        r"(?:(?P<target>.+?) of (?P<within>.+?) is amended )?by striking \"(?P<to_remove_text>.+?)\"\.",
        r"in (?P<target>.+?), by striking \"(?P<to_remove_text>.+?)\" at the end;",
        r"in (?P<target>.+?), by striking \"(?P<to_remove_text>.+?)\";(?: and)?",
        r"by striking \"(?P<to_remove_text>.+?)\"(?:;|\.)",
        r"by striking \"(?P<to_remove_text>.+?)\" at the end of (?P<target>.+?)(?:;|\.)",
        r"in (?P<target>.*) by striking \"(?P<to_remove_text>.+?)\" and inserting \"(?P<to_replace>.+?)\"(?:, and)?",
    ],
    "STRIKE-TEXT-MULTIPLE": [
        r"in (?P<target>.+?), by striking \"(?P<to_remove_text>.+?)\" and inserting \"(?P<to_replace>.+?)\" each place the term appears;"
    ],
    "STRIKE-INSERT-SECTION": [
        r"by striking \"(?P<to_remove_section>.+?)\" and inserting the following:"
    ],
    "INSERT-SECTION-AFTER": [
        r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is (?:further )?amended by inserting after (?P<target_section>(?:sub)?(?:section|paragraph) .+?) the following(?: new paragraphs?)?:",
        r"by inserting after (?P<target>(?:sub)?(?:section|paragraph) .+?) the following(?: new paragraphs?)?:",
    ],
    "INSERT-END": [
        r"At the end of (?P<target>.+?) of (?P<within>.+?),? insert the following:",
        r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is (?:further )?amended by adding at the end the following:",
        r"in (?P<target>.*), by adding at the end the following new (?:sub)?paragraph:",
        r"by adding at the end the following new (?:sub)?paragraph:",
    ],
    "INSERT-TEXT-AFTER": [
        r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is (?:further )?amended.? by inserting \"(?P<to_insert_text>.+?)\" after \"(?P<to_remove_text>.+?)\"(?:; and|\.)",
        r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is (?:further )?amended.? by inserting after \"(?P<to_remove_text>.+?)\" the following: \"(?P<to_insert_text>.+?)\"(?:; and|\.)",
    ],
    "INSERT-TEXT": [
        r"(?:(?P<target>.+?) of (?P<within>.+?) is amended )?by inserting \"(?P<to_insert_text>.+?)\" before \"(?P<target_text>.+?)\".?"
    ],
    "INSERT-TEXT-END": [
        r"in (?P<target>.+?), by adding \"(?P<to_replace>.+?)\" at the end;"
    ],
    "STRIKE-SECTION-INSERT": [
        r"by striking (?P<target>(?:sub)?(?:section|paragraph) .+?) and inserting the following:"
    ],
    "STRIKE-SUBSECTION": [  # Done?
        r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is (?:further )?amended.? by striking (?P<to_remove_section>(?:sub)?(?:section|paragraph) .+?)(?:;|\.)",
        r"by striking (?P<to_remove_section>(?:sub)?(?:section|paragraph) .+?)(?:;|\.)",
    ],
    "STRIKE-PARAGRAPHS-MULTIPLE": [
        r"by striking paragraphs (?P<to_remove_sections>.+?)(?:;|\.)"
    ],
    "REDESIGNATE": [  # Done
        r"by redesignating (?P<target>.+?) as (?P<redesignation>.+?)(;|\.)"
    ],
    "REPEAL": [r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is repealed.?"],
    "EFFECTIVE-DATE": [
        r"The amendments made by this section shall apply to taxable years beginning after (?P<effective_date>.+?)\."
    ],
    "TABLE-OF-CONTENTS": [r"The table of contents (for|of) this Act is as follows:"],
    "TABLE-OF-CHAPTERS": [r"The table of chapters for title (?P<title>)"],
    "INSERT-CHAPTER-AT-END": [
        r"Title (?P<title>\d\d?A?), (?P<document_title>.+), is amended by adding at the end the following new chapter:?"
    ],
    "TERM-DEFINITION": [r"The term \"(?P<term>.+?)\" means (?P<term_def>.+?)."],
}

from unidecode import unidecode

for action in regex_holder:
    regex_holder[action] = [re.compile(x, flags=re.I) for x in regex_holder[action]]


def determine_action(text):
    actions = {}
    text = unidecode(text).replace("--", "-")
    for action in regex_holder:
        c = 0
        for reg in regex_holder[action]:
            res = reg.search(text)
            c = c + 1
            if res is not None:
                gg = res.groupdict()
                gg["REGEX"] = c
                actions[action] = gg
                break
    return actions


SuchCodeRegex = re.compile(r"(Section|paragraph) (?P<section>\d*)\(", re.IGNORECASE)
SubParts = re.compile(r"\((.*?)\)")
DupeFinder = re.compile(r"(\/.{1,}\b)\1")


def parse_such_code(text, title):
    SuchCodeRegex_match = SuchCodeRegex.search(text)
    if SuchCodeRegex_match:
        cite = "/us/usc/t{}/s{}".format(title, SuchCodeRegex_match["section"])
        possibles = SubParts.findall(text)
        if len(possibles) > 0:
            cite += "/" + "/".join(possibles)
        return cite
    return ""


class ActionObject(object):
    def __init__(self, **kwargs):
        self.action_key = kwargs.get("action_key", "")
        self.action = kwargs.get("action", {})
        self.parent_cite = kwargs.get("parent_cite", "")
        self.parsed_cite = kwargs.get("parsed_cite", "")
        self.version_id = kwargs.get("version_id", None)
        self.cited_content = kwargs.get("cited_content", None)
        self.last_title = kwargs.get("last_title", "")
        self.next = kwargs.get("next", None)
        # print(kwargs)

    def set_action(self, action):
        # print(action)
        self.action = action
        within = action.get("within", None)
        target = action.get("target", None)
        if self.parsed_cite == "" and (self.last_title != "") and (target is not None):
            if within is None or within.lower() == "such code":
                # print("suchcode")
                try:
                    self.parsed_cite = parse_such_code(
                        target, self.last_title.split("/")[-1][1:]
                    )
                except:
                    pass
                # print(self.parsed_cite)
        elif target is not None:
            # print('Add target?')
            self.parsed_cite = "/".join(
                [self.parsed_cite] + SubParts.findall(action.get("target", ""))
            )
        target_section = action.get("target_section", None)
        if target_section is not None:
            self.parsed_cite = "/".join(
                [self.parsed_cite] + SubParts.findall(target_section)
            )

        if action.get("to_remove_section", None) is not None:
            found_parts = SubParts.findall(action.get("to_remove_section", ""))
            if not "/".join(found_parts) in self.parsed_cite:
                self.parsed_cite = "/".join([self.parsed_cite] + found_parts)
        found_dupes = DupeFinder.findall(self.parsed_cite)
        if len(found_dupes) > 1:
            log.debug("Found duplicates", found_dupes)
            for dupe in found_dupes[1:]:
                self.parsed_cite = self.parsed_cite.replace(f"{dupe}{dupe}", dupe)
        self.parsed_cite = self.parsed_cite.replace("//", "/")

    def to_dict(self):
        return {self.action_key: self.action, "parsed_cite": self.parsed_cite}
