from zipfile import ZipFile
from typing import List
from lxml import etree
from lxml.etree import Element
from billparser.db.models import (
    LegislationCommittee,
    Legislation,
    LegislationCommitteeAssociation,
    LegislationChamber,
)
from billparser.db.handler import Session


def handle_committees(committee_elements: List[Element]):
    # TODO: Create Committee records using https://github.com/unitedstates/congress-legislators/tree/master/scripts

    session = Session()
    for committee in committee_elements:
        obj = {e.tag: e.text for e in committee}
        existing_obj: LegislationCommittee = (
            session.query(LegislationCommittee)
            .filter(
                LegislationCommittee.system_code == obj["systemCode"],
                LegislationCommittee.chamber == obj["chamber"],
            )
            .first()
        )
        if existing_obj is None:
            new_obj = LegislationCommittee(
                system_code=obj["systemCode"],
                chamber=LegislationChamber(obj["chamber"]),
                name=obj["name"],
                committee_type=obj["type"],
            )
            session.add(new_obj)
            session.commit()
            committee_id = new_obj.legislation_committee_id
        else:
            committee_id = existing_obj.legislation_committee_id

        for subcommitte in committee.xpath(".//subcommittees/item"):
            s_obj = {e.tag: e.text for e in subcommitte}
            existing_obj = (
                session.query(LegislationCommittee)
                .filter(
                    LegislationCommittee.system_code == s_obj["systemCode"],
                    LegislationCommittee.chamber == obj["chamber"],
                )
                .first()
            )
            if existing_obj is None:
                new_obj = LegislationCommittee(
                    system_code=s_obj["systemCode"],
                    chamber=LegislationChamber(obj["chamber"]),
                    name=s_obj["name"],
                    subcommittee=committee_id,
                )
                session.add(new_obj)
                session.commit()

    pass


def parse_status(input_str: str):
    try:
        root = etree.fromstring(input_str)
        bill_element = root.xpath("//bill")[0]
        committees = root.xpath("//billCommittees/item")
        handle_committees(committees)
    except Exception as e:
        print(e)


def parse_archive(f_path: str):
    archive = ZipFile(f_path)
    for file in archive.namelist():
        r = archive.open(file, "r").read()
        parse_status(r)