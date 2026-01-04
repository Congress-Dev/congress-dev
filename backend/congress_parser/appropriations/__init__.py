import spacy
from spacy.matcher import Matcher

from congress_db.models import Appropriation, LegislationContent
nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)
# to remain available until
fy_pattern = [
    {"LOWER": "to", "OP": "?"},
    {"LOWER": "remain", "OP": "?"},
    {"LOWER": "available", "OP": "?"},
    {"LOWER": "until", "OP": "?"},
    {"LOWER": "fiscal"},
    {"LOWER": "year", "OP": "?"},  # Optional "year" to match both "fiscal year" and "fiscal years"
    {"LOWER": "years", "OP": "?"},  # Optional "years" to match both "fiscal year" and "fiscal years"
    {"IS_DIGIT": True},  # The start year
    {"LOWER": "through", "OP": "?"},  # Optional "through" for ranges
    {"IS_DIGIT": True, "OP": "?"}  # The end year (optional, for ranges)
]
money_pattern = [{"ORTH": "$", "OP": "?"}, {"LIKE_NUM": True, "OP": "+"}]

matcher.add("FISCAL_YEAR_PATTERN", [fy_pattern])
matcher.add("MONEY_PATTERN", [money_pattern])

def filter_contained_matches(matches):
    filtered_matches = []
    seen_starts = set()
    for match_id, start, end in sorted(matches, key=lambda x: (x[1], -x[2])):
        if start not in seen_starts:
            filtered_matches.append((match_id, start, end))
            seen_starts.update(range(start, end))
    return filtered_matches

def calculate_appropriation(leg_content: LegislationContent):
    if leg_content.content_str is None:
        return None
    doc = nlp(leg_content.content_str)
    matches = matcher(doc)
    filtered_matches = filter_contained_matches(matches)

    fiscal_years = []
    amount = None
    until_expended = False
    new_spending = "authorized to be appropriated" in leg_content.content_str
    # TODO: If through is present, then we should add all years in between
    for match_id, start, end in filtered_matches:
        span = doc[start:end]
        if doc.vocab.strings[match_id] == "FISCAL_YEAR_PATTERN":
            if "to remain available until" in span.text:
                until_expended = True
            for token in doc[start:end]:
                if token.like_num:
                    fiscal_years.append(int(token.text))
            if "through" in span.text:
                fiscal_years = list(range(fiscal_years[0], fiscal_years[1] + 1))
        elif doc.vocab.strings[match_id] == "MONEY_PATTERN":
            amt = float(span.text.replace("$", "").replace(",", ""))
            if amt < 10000:
                print("Skipping small amount", amt)
            else:
                amount = amt
    # print("="*10)
    if amount is None:
        # print("Did not find an amount")
        return None
    return Appropriation(
        legislation_content_id=leg_content.legislation_content_id,
        fiscal_years=fiscal_years,
        amount=amount,
        until_expended=until_expended,
        new_spending=new_spending,
    )