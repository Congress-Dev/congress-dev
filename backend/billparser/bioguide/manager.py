import requests
from typing import List
import logging
import zipfile
import json
import io
import json

from billparser.db.handler import Session
from billparser.db.models import Legislator
from billparser.bioguide.types import BioGuideMember

BULK_BIOGUIDE_URL = "https://bioguide.congress.gov/bioguide/data/BioguideProfiles.zip"
SENATE_LIST_URL = "https://www.senate.gov/legislative/LIS_MEMBER/cvc_member_data.xml"

class BioGuideImporter:
    def __init__(
        self, bulk_bioguide_url=BULK_BIOGUIDE_URL, senate_list_url=SENATE_LIST_URL
    ):
        self.bulk_bioguide_url = bulk_bioguide_url
        self.senate_list_url = senate_list_url
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
        # with self._download_zip() as z:
        with zipfile.ZipFile('./.sources/BioguideProfiles.zip', 'r') as z:
            names = z.namelist()
            logging.debug(
                f"Found {len(names)} files in zip", extra={"name_count": len(names)}
            )
            for filename in names:
                with z.open(filename) as f:
                    jdata = json.load(f)
                    if jdata.get('data') is None:
                        legis = BioGuideMember(**jdata)
                    else:
                        legis = BioGuideMember(**jdata.get('data'))
                    items.append(legis)

        return items

    def run_metadata(self):
        member_lis_lookup = {}

        with open('./.sources/legislators-current.json', 'r') as f:
            for legislator in json.load(f):
                if legislator['id'].get('lis') is not None:
                    member_lis_lookup[legislator['id'].get('bioguide')] = legislator['id'].get('lis')

        with open('./.sources/legislators-historical.json', 'r') as f:
            for legislator in json.load(f):
                if legislator['id'].get('lis') is not None:
                    member_lis_lookup[legislator['id'].get('bioguide')] = legislator['id'].get('lis')

        return member_lis_lookup

    def download_to_database(self) -> None:
        legislators = self.run_import()
        lis_lookup = self.run_metadata()

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

                try:
                    state = legislator.jobPositions[-1].congressAffiliation.represents.regionCode
                except:
                    state = None

                try:
                    image_url = "https://bioguide.congress.gov/photo/"
                    image_url += legislator.asset[-1]['contentUrl'].split("/")[-1]
                    image_source = legislator.asset[-1]['creditLine']
                except:
                    image_url = None
                    image_source = None

                record_data = {}

                if lis_lookup.get(legislator.usCongressBioId, None):
                    record_data['lis_id'] = lis_lookup.get(legislator.usCongressBioId, None)
                if legislator.usCongressBioId:
                    record_data['bioguide_id'] = legislator.usCongressBioId
                if legislator.nickName or legislator.unaccentedGivenName or legislator.givenName:
                    record_data['first_name'] = legislator.nickName or legislator.unaccentedGivenName or legislator.givenName
                if legislator.unaccentedFamilyName or legislator.familyName:
                    record_data['last_name'] = legislator.unaccentedFamilyName or legislator.familyName
                if legislator.unaccentedMiddleName or legislator.middleName:
                    record_data['middle_name'] = legislator.unaccentedMiddleName or legislator.middleName
                if party:
                    record_data['party'] = party
                if state:
                    record_data['state'] = state
                if image_url:
                    record_data['image_url'] = image_url
                if image_source:
                    record_data['image_source'] = image_source
                if legislator.profileText:
                    record_data['profile'] = legislator.profileText

                existing_record = self.session.query(Legislator).filter(Legislator.bioguide_id == legislator.usCongressBioId).first()
                if existing_record is None:
                    new_legislator = Legislator(**record_data)
                    db_items.append(new_legislator)
                else:
                    for key, value in record_data.items():
                        setattr(existing_record, key, value)

            self.session.add_all(db_items)
            self.session.commit()
        logging.debug("Finished adding legislators to database")