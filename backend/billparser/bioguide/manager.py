import requests
from typing import List
import logging
import zipfile
import json
import io

from billparser.db.handler import Session
from billparser.db.models import Legislator
from billparser.bioguide.types import BioGuideMember

BULK_BIOGUIDE_URL = "https://bioguide.congress.gov/bioguide/data/BioguideProfiles.zip"
CURRENT_LEGIS_URL = (
    "https://theunitedstates.io/congress-legislators/legislators-current.json"
)


class BioGuideImporter:
    def __init__(
        self, bulk_bioguide_url=BULK_BIOGUIDE_URL, current_legis_url=CURRENT_LEGIS_URL
    ):
        self.bulk_bioguide_url = bulk_bioguide_url
        self.current_legis_url = current_legis_url
        self.session = Session()

    def _download_zip(self) -> zipfile.ZipFile:
        logging.debug("Starting download of bulk bioguide data")
        r = requests.get(self.bulk_bioguide_url)
        logging.debug(
            "Finished download of bulk bioguide data",
            extra={"headers": r.headers, "status_code": r.status_code},
        )
        z = zipfile.ZipFile(io.BytesIO(r.content))
        return z

    def run_import(self) -> List[BioGuideMember]:
        items = []
        with self._download_zip() as z:
            names = z.namelist()
            logging.debug(
                f"Found {len(names)} files in zip", extra={"name_count": len(names)}
            )
            for filename in names:
                with z.open(filename) as f:
                    legis = BioGuideMember(**json.load(f))
                    items.append(legis)
        return items

    def download_to_database(self) -> None:
        legislators = self.run_import()
        db_items = []
        with self.session.begin():
            for legislator in legislators:
               
                try:
                    # TODO: Make this look nicer, but not everybody has a party
                    # TODO: If we're modeling this for real, we'd want to have a table for the jobs
                    # TODO: What can I do to extract the image url?
                    party = legislator.jobPositions[-1].congressAffiliation.partyAffiliation[0].party.name
                except:
                    party = None
                 # TODO: Get state and region
                new_legislator = Legislator(
                    bioguide_id = legislator.usCongressBioId,
                    first_name = legislator.unaccentedGivenName or legislator.givenName,
                    last_name = legislator.unaccentedFamilyName or legislator.familyName,
                    middle_name = legislator.unaccentedMiddleName or legislator.middleName,
                    party = party,
                )
                db_items.append(new_legislator)
            self.session.add_all(db_items)
            self.session.commit()
        logging.debug("Finished adding legislators to database")