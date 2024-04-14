from lxml import etree
import lxml
import logging
from typing import List, Dict
from billparser.db.models import LegislationSponsorship


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
        new_sponsor = LegislationSponsorship(
            legislator_bioguide_id=sponsor_element.attrib["name-id"],
            legislation_id=legislation_id,
            cosponsor=False,
        )
        session.add(new_sponsor)
        sponsors.append(new_sponsor)
    for sponsor_element in cosponsor_elements:
        new_sponsor = LegislationSponsorship(
            legislator_bioguide_id=sponsor_element.attrib["name-id"],
            legislation_id=legislation_id,
            cosponsor=True,
        )
        session.add(new_sponsor)
        sponsors.append(new_sponsor)
    logging.info(f"Extracted {len(sponsors)} sponsors from form", extra={"num_sponsors": len(sponsors)})
    return sponsors
