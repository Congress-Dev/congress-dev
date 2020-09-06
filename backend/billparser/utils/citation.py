import re


def resolve_citations(text: str, title_num: str) -> str:
    """
        Puts xml tags around all citations
    """
    title_cites = [
        r"\W(sections? (?P<inner>.*?) of (?P<title>(?:this )?title(?:\d\d?)?))\W",
        r"\W(section (?P<section>\d*)(?P<subsection>\(.*?\))? of (?P<title>this title))\W",
        r"\W(section (?P<section>\d*)(?P<subsection>\(.*?\))? of title (?P<title>\d\d?))\W",
        r"\W(section (?P<section>\d*))\W",
    ]

    def spit_out_xml(t, s, text):
        return f'<usccite src="/usc/{t}/{s}">{text}</usccite>'

    subsect_reg = r"(?P<section>\d+)?(?P<subsections>(?:\(.*?\))*)?"
    for regex_str in title_cites:
        result = ""
        matches = re.search(regex_str, text, re.MULTILINE + re.IGNORECASE)
        if matches is not None:
            group_matches = matches.groupdict()
            last_ind = 0
            title_num_m = group_matches.get("title", "this title")
            if title_num_m == "this title":
                title_num_m = title_num
            if "section" in group_matches:
                sec_num = group_matches.get("section")

                end_ind = 0
                if "title" in group_matches:
                    end_ind = matches.end("title")
                else:
                    end_ind = matches.end("section")
                p_str = spit_out_xml(
                    title_num_m,
                    sec_num,
                    f"section {text[matches.start('section'):end_ind]}",
                )
                # TODO: Is recursion the best option here?
                return (
                    resolve_citations(
                        text[last_ind : matches.start("section") - len("section ")],
                        title_num_m,
                    )
                    + p_str
                    + resolve_citations(text[end_ind:], title_num_m)
                )
            elif "inner" in group_matches:
                inner_ind = matches.start("inner")
                end_ind = matches.end("inner")
                inner_str = group_matches.get("inner")
                inner_matches = re.finditer(subsect_reg, inner_str)
                current_section = None
                p_str = ""
                last_inner_ind = 0
                for sub_match in inner_matches:
                    if sub_match.group(0) != "":
                        g_dict = sub_match.groupdict()
                        current_section = g_dict.get("section") or current_section
                        subsect = g_dict.get("subsections")
                        p_str += inner_str[
                            last_inner_ind : sub_match.start()
                        ] + spit_out_xml(
                            title_num_m,
                            current_section,
                            inner_str[sub_match.start() : sub_match.end()],
                        )
                        last_inner_ind = sub_match.end()
                return (
                    resolve_citations(
                        text[last_ind : matches.start("inner")], title_num_m
                    )
                    + p_str
                    + resolve_citations(text[end_ind:], title_num_m)
                )
    return text


def remove_citations(text: str) -> str:
    return re.sub(r"\<usccite src.*?\"\>", "", text, count=200).replace("</usccite>", "")