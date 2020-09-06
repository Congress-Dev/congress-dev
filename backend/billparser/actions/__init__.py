import re
from billparser.logger import log
from unidecode import unidecode


# TODO: This whole file is some honkin bullshit. It's entirely unsustainable, but at the same time, unless I can get them to follow standards, I'm not sure
# I can actually do anything else but maintain a long ass list of regexes.


# These regexes all have named capture groups, because they are incredibly useful
# The capture groups are typically consistent, especially when the same functions are used between different 'actions'
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
        r"(?:in (?P<target>.*),)?\s?by striking \"(?P<to_remove_text>.+?)\" and inserting \"(?P<to_replace>.+?)\"(?:\.|;)",
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
        r"(?P<target>.+?)(?: of (?P<within>.+?),?)? is (?:further )?amended by inserting after (?P<target_section>(?:sub)?(?:section|paragraph) .+?) the following(?: new (paragraph|section)s?)?:",
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
        r"^in (?P<target>.+?), by inserting \"(?P<to_insert_text>.+?)\" after \"(?P<to_remove_text>.+?)\";?",
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
    "TERM-DEFINITION": [
        r"The term \"(?P<term>.+?)\" means (?P<term_def>.+?).",
        r"The term (?P<term>.+?) means (?P<term_def>.+?).",
    ],
    "DATE": [
        r"(?:(?P<month>(?:Jan|Febr)uary|March|April|May|Ju(?:ne|ly)|August|(?:Septem|Octo|Novem|Decem)ber) (?P<day>\d\d?)\, (?P<year>\d\d\d\d))"
    ],
    "FINANCIAL": [
        r"(?P<dollar>\$\s?(\d{1,3}\,?)(\d{3}\,?)*(\.\d\d)?)"
    ]
}

SuchCodeRegex = re.compile(r"(Section|paragraph) (?P<section>\d*)\(", re.IGNORECASE)
SubParts = re.compile(r"\((.*?)\)")
DupeFinder = re.compile(r"(\/.{1,}\b)\1")


for action in regex_holder:
    regex_holder[action] = [re.compile(x, flags=re.I) for x in regex_holder[action]]


def determine_action(text: str) -> dict:
    """
    Parses the input string against all the regexes
    Searches each action's regexes until it finds one
    The order in which the regexes are placed are important, because the most general ones need to be last
    Especially if there is information in the more specific ones that is important for action.

    Args:
        text (str): Input bill clause string

    Returns:
        dict: A dict of the matching action regexes
    """
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


def parse_such_code(text: str, title: str) -> str:
    """
    Sometimes clauses in a bill will reference "such code", which means we've already been given the Chapter
    and all we have to do is attempt to match up the section to that Chapter

    Args:
        text (str): String containing the such code reference
        title (str): Chapter

    Returns:
        str: A usc cite according to the such code logic
    """
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
        self.legislation_content = kwargs.get("legislation_content", None)
        self.diff_id = None
        # print(kwargs)

    def set_diff_id(self, diff_id):
        self.diff_id = diff_id

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
        return {self.action_key: self.action, "parsed_cite": self.parsed_cite, "diff_id": self.diff_id}
