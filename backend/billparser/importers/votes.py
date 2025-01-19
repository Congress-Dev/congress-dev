from datetime import datetime
import requests
from lxml import etree
from lxml.etree import Element
import json
import logging
import re
import time

from billparser.db.handler import Session
from billparser.db.models import LegislationVote, LegislatorVote, LegislatorVoteType, Legislation, LegislationChamber, Legislator, Congress
from billparser.bioguide.manager import BioGuideImporter

def calculate_congress_from_year() -> int:
    current_year = datetime.now().year
    congress = ((current_year - 2001) // 2) + 107
    return congress

def calculate_session_from_year() -> int:
    current_year = datetime.now().year
    current_congress = ((current_year - 2001) // 2) + 107
    last_congress = ((current_year - 2001 - 1) // 2) + 107

    if current_congress != last_congress:
        return 1
    else:
        return 2

def get_latest_house_rollcall(session) -> int:
    legislation_vote = (session
        .query(LegislationVote)
        .filter(LegislationVote.chamber == LegislationChamber.House)
        .order_by(LegislationVote.number.desc())
        .first()
    )

    if legislation_vote is None:
        return 0
    else:
        return legislation_vote.number

def get_latest_senate_rollcall(session) -> int:
    legislation_vote = (session
        .query(LegislationVote)
        .filter(LegislationVote.chamber == LegislationChamber.Senate)
        .order_by(LegislationVote.number.desc())
        .first()
    )

    if legislation_vote is None:
        return 0
    else:
        return legislation_vote.number

def download_house_rollcall(session, formatted, congress):
    HOUSE_ROLL_TEMPLATE = "https://clerk.house.gov/evs/{year}/roll{h_index:03}.xml" # Index 3 digits

    rec = []

    while True:
        print("-"*50)
        formatted['h_index'] = formatted['h_index'] + 1

        url = HOUSE_ROLL_TEMPLATE.format(**formatted)
        logging.info(f"Fetching House rollcall vote from {url}")
        resp = requests.get(url)

        if resp.status_code == 404:
            logging.info(f"Completed fetch at {formatted['h_index']} with 404 error")
            break
        else:
            logging.info(f"Parsing rollcall {formatted['h_index']} votes")

            root: Element = etree.fromstring(resp.text.encode('utf-8'))
            vote_metadata = root.xpath("//vote-metadata")
            if vote_metadata:
                db_items = []

                by_total = {}
                by_party = {}
                by_legislator = {}

                vote_date = root.xpath("//action-date/text()")[0]
                vote_time = root.xpath("//action-time/text()")[0]
                vote_question = root.xpath("//vote-question/text()")[0]
                vote_type = root.xpath("//vote-type/text()")[0]
                vote_result = root.xpath("//vote-result/text()")[0]

                legislation_number = None
                legislation_number_data = root.xpath("//legis-num/text()")

                if len(legislation_number_data) > 0:
                    legislation_pattern = r"H R (\d+)"
                    legislation_match = re.match(legislation_pattern, legislation_number_data[0])

                    if legislation_match:
                        legislation_number = legislation_match.group(1)
                    else:
                        logging.info(f"Skipping rollcall {formatted['h_index']} due to unsupported legislation_number {legislation_number_data[0]}")
                        continue
                else:
                    logging.info(f"Skipping rollcall {formatted['h_index']} due to missing legislation_number")
                    continue

                if "YEA-AND-NAY" not in vote_type:
                    logging.info(f"Skipping rollcall {formatted['h_index']} due to unsupported vote_type {vote_type}")
                    continue

                totals_data = root.xpath("//totals-by-vote")
                if len(totals_data) == 1:
                    by_total = {
                        'yay': int(totals_data[0].xpath("./yea-total/text()")[0]),
                        'nay': int(totals_data[0].xpath("./nay-total/text()")[0]),
                        'present': int(totals_data[0].xpath("./present-total/text()")[0]),
                        'abstain': int(totals_data[0].xpath("./not-voting-total/text()")[0]),
                    }

                party_data = root.xpath("//totals-by-party")
                if len(party_data) > 0:
                    for party in party_data:
                        party_type = party.xpath("./party/text()")[0]  # Get the party name
                        by_party[party_type] = {
                            'yay': int(party.xpath("./yea-total/text()")[0]),
                            'nay': int(party.xpath("./nay-total/text()")[0]),
                            'present': int(party.xpath("./present-total/text()")[0]),
                            'abstain': int(party.xpath("./not-voting-total/text()")[0]),
                        }

                vote_data = root.xpath("//recorded-vote")
                if len(vote_data) > 0:
                    for vote in vote_data:
                        legislator = vote.xpath('./legislator')[0]
                        by_legislator[legislator.get('name-id')] = {
                            'vote': LegislatorVoteType.from_string(vote.xpath('./vote/text()')[0])
                        }

                if by_total and by_party and by_legislator:
                    legislation = (session
                        .query(Legislation)
                        .filter(Legislation.number == legislation_number)
                        .filter(Legislation.chamber == 'House')
                        .filter(Legislation.congress_id == congress)
                        .first())

                    if legislation is None:
                        logging.error(f"Could not find matching legislation for H.R.{legislation_number}")
                        continue

                    legislation_vote_data = {
                        'number': formatted['h_index'],
                        'datetime': datetime.strptime(f"{vote_date} {vote_time}", "%d-%b-%Y %I:%M %p"),
                        'legislation_id': legislation.legislation_id,
                        'question': vote_question,
                        'independent': json.dumps(by_party['Independent']),
                        'republican': json.dumps(by_party['Republican']),
                        'democrat': json.dumps(by_party['Democratic']),
                        'total': json.dumps(by_total),
                        'passed': (vote_result == 'Passed'),
                        'chamber': LegislationChamber.House,
                        'congress_id': congress,
                    }

                    legislation_vote = LegislationVote(**legislation_vote_data)
                    rec.append(legislation_vote)

                    try:
                        session.add(legislation_vote)
                        session.commit()
                    except:
                        logging.error(f"Could not commit LegislationVote to database")
                        continue

                    legislator_votes = []
                    for bioguide_id, vote_info in by_legislator.items():
                        legislator = (session
                            .query(Legislator)
                            .filter(Legislator.bioguide_id == bioguide_id)
                            .first())

                        if legislator is None:
                            logging.info(f"Missing legislator information for {bioguide_id}")
                            continue

                        legislator_vote_data = {
                            'legislation_vote_id': legislation_vote.id,
                            'legislator_bioguide_id': bioguide_id,
                            **vote_info
                        }

                        legislator_vote = LegislatorVote(**legislator_vote_data)
                        legislator_votes.append(legislator_vote)

                    try:
                        session.add_all(legislator_votes)
                        session.commit()
                    except:
                        logging.error(f"Could not commit LegislatorVote to database")

                    logging.info(f"Finished parsing rollcall {formatted['h_index']}")
                else:
                    logging.info(f"Skipping rollcall {formatted['h_index']} due to missing vote data")

    return rec

def download_senate_rollcall(session, formatted, congress):
    SENATE_ROLL_TEMPLATE = "https://www.senate.gov/legislative/LIS/roll_call_votes/vote{congress}{session}/vote_{congress}_{session}_{s_index:05}.xml" #Index 5 digits
    LEGIS_LOOKUP = get_legislator_lookup()

    rec = []

    while True:
        print("-"*50)
        formatted['s_index'] = formatted['s_index'] + 1

        url = SENATE_ROLL_TEMPLATE.format(**formatted)
        logging.info(f"Fetching Senate rollcall vote from {url}")
        resp = requests.get(url)

        if resp.headers.get('Content-Type') != 'text/xml':
            logging.info(f"Completed fetch at {formatted['s_index']} with 404 error")
            break
        else:
            logging.info(f"Parsing rollcall {formatted['s_index']} votes")

            root: Element = etree.fromstring(resp.text.encode('utf-8'))
            if root is not None:
                db_items = []

                by_total = {}
                by_party = {}
                by_legislator = {}

                vote_date = root.xpath("//vote_date/text()")[0]
                vote_question = root.xpath("//question/text()")[0]
                vote_result = root.xpath("//vote_result/text()")[0]

                legislation_number = None
                legislation_number_data = root.xpath("//document//document_name/text()")

                if len(legislation_number_data) > 0:
                    legislation_pattern = r"S. (\d+)"
                    legislation_match = re.match(legislation_pattern, legislation_number_data[0])

                    if legislation_match:
                        legislation_number = legislation_match.group(1)
                    else:
                        logging.info(f"Skipping rollcall {formatted['s_index']} due to unsupported legislation_number {legislation_number_data[0]}")
                        continue
                else:
                    logging.info(f"Skipping rollcall {formatted['s_index']} due to missing legislation_number")
                    continue

                totals_data = root.xpath("//count")
                if len(totals_data) == 1:
                    by_total = {
                        'yay': int(totals_data[0].xpath("./yeas/text()")[0]),
                        'nay': int(totals_data[0].xpath("./nays/text()")[0]),
                        'present': int(totals_data[0].xpath("./present/text()")[0] if len(totals_data[0].xpath("./present/text()")) > 0 else 0),
                        'abstain': int(totals_data[0].xpath("./absent/text()")[0] if len(totals_data[0].xpath("./absent/text()")) > 0 else 0),
                    }

                for party in ['D', 'R', 'I']:
                    by_party[party] = {
                        'yay': 0,
                        'nay': 0,
                        'present': 0,
                        'abstain': 0,
                    }

                vote_data = root.xpath("//members//member")
                if len(vote_data) > 0:
                    for vote in vote_data:
                        legislator = vote.xpath('./lis_member_id/text()')[0]
                        party = vote.xpath('./party/text()')[0]
                        vote = LegislatorVoteType.from_string(vote.xpath('./vote_cast/text()')[0])

                        by_legislator[legislator] = { 'vote': vote }
                        by_party[party][vote.value] = by_party[party][vote.value] + 1

                if by_total and by_party and by_legislator:
                    legislation = (session
                        .query(Legislation)
                        .filter(Legislation.number == legislation_number)
                        .filter(Legislation.chamber == 'Senate')
                        .filter(Legislation.congress_id == congress)
                        .first())

                    if legislation is None:
                        logging.error(f"Could not find matching legislation for S.{legislation_number}")
                        continue

                    legislation_vote_data = {
                        'number': formatted['s_index'],
                        'datetime': datetime.strptime(vote_date, "%B %d, %Y, %I:%M %p"),
                        'legislation_id': legislation.legislation_id,
                        'question': vote_question,
                        'independent': json.dumps(by_party['I']),
                        'republican': json.dumps(by_party['R']),
                        'democrat': json.dumps(by_party['D']),
                        'total': json.dumps(by_total),
                        'passed': (' Agreed' in vote_result),
                        'chamber': LegislationChamber.Senate,
                        'congress_id': congress,
                    }

                    legislation_vote = LegislationVote(**legislation_vote_data)
                    rec.append(legislation_vote)

                    try:
                        session.add(legislation_vote)
                        session.commit()
                    except:
                        logging.error(f"Could not commit LegislationVote to database")
                        continue

                    legislator_votes = []
                    for lis_id, vote_info in by_legislator.items():
                        legislator = (session
                            .query(Legislator)
                            .filter(Legislator.lis_id == lis_id)
                            .first())

                        if legislator is None:
                            logging.info(f"Missing legislator information for {lis_id}")
                            continue

                        legislator_vote_data = {
                            'legislation_vote_id': legislation_vote.id,
                            'legislator_bioguide_id': legislator.bioguide_id,
                            **vote_info
                        }

                        legislator_vote = LegislatorVote(**legislator_vote_data)
                        legislator_votes.append(legislator_vote)

                    try:
                        session.add_all(legislator_votes)
                        session.commit()
                    except:
                        logging.error(f"Could not commit LegislatorVote to database")

                    logging.info(f"Finished parsing rollcall {formatted['s_index']}")
                else:
                    logging.info(f"Skipping rollcall {formatted['s_index']} due to missing vote data")

    return rec

def send_message(text):
    if webhook_url is not None:
        import requests

        requests.post(webhook_url, json={"content": text})

def download_to_database():
    CURRENT_CONGRESS = None

    session = Session()
    congress = (session
        .query(Congress)
        .filter(Congress.session_number == calculate_congress_from_year())
        .first())

    if congress is not None:
        CURRENT_CONGRESS = congress.congress_id
        logging.info(f"Fetching legislation for congress {CURRENT_CONGRESS}")
    else:
        logging.error("Failed to fetch the current Congress object")
        return

    formatted = {
        'year': datetime.now().year,
        'congress': calculate_congress_from_year(),
        'session': calculate_session_from_year(),
        'h_index': get_latest_house_rollcall(session),
        's_index': get_latest_senate_rollcall(session),
    }

    house_rec = download_house_rollcall(session, formatted, CURRENT_CONGRESS)
    senate_rec = download_senate_rollcall(session, formatted, CURRENT_CONGRESS)

    send_message(
        f"Added {len(house_rec)} House and {len(senate_rec)} Senate rollcall votes today"
    )

if __name__ == "__main__":
    download_to_database()
