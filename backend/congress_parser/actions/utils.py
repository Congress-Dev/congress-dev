import re


def strike_emulation(
    to_strike: str, to_replace: str, target: str, multiple: bool = True
) -> str:
    """
    Handles emulating the strike text behavior for a given string

    Args:
        to_strike (str): Text to search for
        to_replace (str): Text to replace with, if any
        target (str): Text to look in

    Returns:
        str: The result of the replacement
    """
    start_boi = r"(\b)"
    # target = remove_citations(target)
    if "$" not in to_strike and ")" not in to_strike and "(" not in to_strike:
        return re.sub(
            r"{}({})(?:\b)?".format(start_boi, re.escape(to_strike)),
            to_replace,
            target,
        )
    elif to_strike in target:
        # Remove spaces before commas?
        return target.replace(to_strike, to_replace, -1 if multiple else 1).replace(
            " ,", ","
        )
    return target