import logging
import requests
from typing import List, Dict
from billparser.db.models import LegislationSponsorship, Congress
from os import environ

CONGRESS_API_KEY = environ.get('CONGRESS_API_KEY')

def extract_sponsors_from_form(
    form_element, legislation_id: int, session
) -> List[Dict]:
    """
    Extracts the sponsors from the form element
    :param form_element: The form element
    :return: A list of sponsors
    """
    sponsors = []
    sponsor_elements = form_element.findall(".//sponsor")
    cosponsor_elements = form_element.findall(".//cosponsor")
    for sponsor_element in sponsor_elements:
        parent = session.query(Legislator).filter_by(bioguide_id=sponsor_element.attrib["name-id"]).first()
        if parent is not None:
            new_sponsor = LegislationSponsorship(
                legislator_bioguide_id=sponsor_element.attrib["name-id"],
                legislation_id=legislation_id,
                cosponsor=False,
            )
            session.add(new_sponsor)
            sponsors.append(new_sponsor)
    for sponsor_element in cosponsor_elements:
        parent = session.query(Legislator).filter_by(bioguide_id=sponsor_element.attrib["name-id"]).first()
        if parent is not None:
            new_sponsor = LegislationSponsorship(
                legislator_bioguide_id=sponsor_element.attrib["name-id"],
                legislation_id=legislation_id,
                cosponsor=True,
            )
            session.add(new_sponsor)
            sponsors.append(new_sponsor)
    logging.info(f"Extracted {len(sponsors)} sponsors from form", extra={"num_sponsors": len(sponsors)})
    return sponsors

def extract_sponsors_from_api(congress, bill_obj, legislation_id, session) -> List[Dict]:
    chamberLookup = {
        "House": "hr",
        "Senate": "s",
    }

    congress_number = session.query(Congress).filter_by(congress_id=congress).first().session_number;
    url = f"https://api.congress.gov/v3/bill/{congress_number}/{chamberLookup[bill_obj['chamber']]}/{bill_obj['bill_number']}?format=json&api_key={CONGRESS_API_KEY}"

    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            bill = data.get('bill')
            sponsors = bill.get('sponsors')

            bioguide_id = sponsors[0].get('bioguideId')
            if bioguide_id is not None:
                new_sponsor = LegislationSponsorship(
                    legislator_bioguide_id=bioguide_id,
                    legislation_id=legislation_id,
                    cosponsor=False,
                )
                session.add(new_sponsor)
                session.commit()
                sponsors.append(new_sponsor)
        except Exception as e:
            logging.error("Uncaught exception", exc_info=e)
    else:
        logging.error(f"Failed to fetch data. Status code: {response.status_code}")
        logging.error(response.text)