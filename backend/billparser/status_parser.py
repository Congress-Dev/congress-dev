from zipfile import ZipFile
from typing import List
from lxml import etree
from lxml.etree import Element

from dateutil.parser import parse

from billparser.db.models import (
    LegislationCommittee,
    Legislation,
    LegislationCommitteeAssociation,
    LegislationChamber,
    Congress,
    LegislativePolicyArea,
    LegislativePolicyAreaAssociation,
    LegislativeSubject,
    LegislativeSubjectAssociation,
)
from billparser.db.handler import Session


def _ensure_committee_link(committee_id, legislation_id, referred_date, discharge_date):
    session = Session()
    existing_obj: LegislationCommitteeAssociation = (
        session.query(LegislationCommitteeAssociation)
        .filter(
            LegislationCommitteeAssociation.legislation_committee_id == committee_id,
            LegislationCommitteeAssociation.legislation_id == legislation_id,
        )
        .first()
    )
    if existing_obj is None:
        new_obj = LegislationCommitteeAssociation(
            legislation_committee_id=committee_id,
            legislation_id=legislation_id,
            referred_date=parse(referred_date),
            discharge_date=parse(discharge_date),
            congress_id=None,
        )
        session.add(new_obj)
    else:
        existing_obj.discharge_date = parse(discharge_date)
    session.commit()


def handle_committees(committee_elements: List[Element], bill_object: Legislation):
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
        committee_activities = committee.xpath(".//activities/item")
        com_referred_date = None
        com_discharge_date = None
        for activity in committee_activities:
            a_obj = {e.tag: e.text for e in activity}
            if a_obj["name"].lower() == "referred to":
                com_referred_date = a_obj["date"]
            elif a_obj["name"].lower() == "discharged from":
                com_discharge_date = a_obj["date"]
        _ensure_committee_link(
            committee_id,
            bill_object.legislation_id,
            com_referred_date,
            com_discharge_date,
        )

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
                subcommitte_id = new_obj.legislation_committee_id
            else:
                subcommitte_id = existing_obj.legislation_committee_id
            subcommittee_activities = subcommitte.xpath(".//activities/item")
            scom_referred_date = None
            scom_discharge_date = None
            for activity in subcommittee_activities:
                a_obj = {e.tag: e.text for e in activity}
                if a_obj["name"].lower() == "referred to":
                    scom_referred_date = a_obj["date"]
                elif a_obj["name"].lower() == "discharged from":
                    scom_discharge_date = a_obj["date"]
            _ensure_committee_link(
                subcommitte_id,
                bill_object.legislation_id,
                scom_referred_date,
                scom_discharge_date,
            )
    pass


def handle_subject(subject: Element, bill_object: Legislation):
    session = Session()
    existing_obj: LegislativeSubject = (
        session.query(LegislativeSubject)
        .filter(LegislativeSubject.subject == subject.text)
        .first()
    )
    if existing_obj is None:
        new_obj = LegislativeSubject(
            subject=subject.text, congress_id=bill_object.congress_id
        )
        session.add(new_obj)
        session.commit()
        subject_id = new_obj.legislative_subject_id
    else:
        subject_id = existing_obj.legislative_subject_id

    existing_obj: LegislativeSubjectAssociation = (
        session.query(LegislativeSubjectAssociation)
        .filter(
            LegislativeSubjectAssociation.legislation_id == bill_object.legislation_id,
            LegislativeSubjectAssociation.legislative_subject_id == subject_id,
        )
        .first()
    )
    if existing_obj is None:
        new_obj = LegislativeSubjectAssociation(
            legislation_id=bill_object.legislation_id,
            legislative_subject_id=subject_id,
        )
        session.add(new_obj)
        session.commit()


def handle_policy_area(policy_area: Element, bill_object: Legislation):
    session = Session()
    existing_obj: LegislativePolicyArea = (
        session.query(LegislativePolicyArea)
        .filter(LegislativePolicyArea.name == policy_area.text)
        .first()
    )
    if existing_obj is None:
        new_obj = LegislativePolicyArea(
            name=policy_area.text, congress_id=bill_object.congress_id
        )
        session.add(new_obj)
        session.commit()
        policy_area_id = new_obj.legislative_policy_area_id
    else:
        policy_area_id = existing_obj.legislative_policy_area_id
    existing_obj: LegislativePolicyAreaAssociation = (
        session.query(LegislativePolicyAreaAssociation)
        .filter(
            LegislativePolicyAreaAssociation.legislation_id
            == bill_object.legislation_id,
            LegislativePolicyAreaAssociation.legislative_policy_area_id
            == policy_area_id,
        )
        .first()
    )
    if existing_obj is None:
        new_obj = LegislativePolicyAreaAssociation(
            legislation_id=bill_object.legislation_id,
            legislative_policy_area_id=policy_area_id,
        )
        session.add(new_obj)
        session.commit()


def parse_status(input_str: str):
    try:
        root = etree.fromstring(input_str)
        bill_element = root.xpath("//bill")[0]
        actions = root.xpath("//actions/item")
        committees = root.xpath("//billCommittees/item")
        policy_area = root.xpath("//policyArea/name")
        subjects = root.xpath("//legislativeSubjects/item/name")
        bill_info = {
            e.tag: e.text
            for e in bill_element
            if e.tag in ["billNumber", "originChamber", "type", "congress", "number"]
        }
        # print(bill_info)
        session = Session()
        congress: Congress = (
            session.query(Congress)
            .filter(Congress.session_number == int(bill_info["congress"]))
            .first()
        )
        # print(congress)
        # TODO: Filter on Legislation type, congress
        matching_bill: Legislation = (
            session.query(Legislation)
            .filter(
                Legislation.chamber == LegislationChamber(bill_info["originChamber"]),
                Legislation.number == bill_info["number"],
                Legislation.congress_id == congress.congress_id,
            )
            .first()
        )
        if matching_bill is None:
            print("Did not find bill")
            return
            # matching_bill = Legislation(legislation_id=1)
        handle_committees(committees, matching_bill)
        if policy_area:
            handle_policy_area(policy_area[0], matching_bill)
        for subject in subjects:
            handle_subject(subject, matching_bill)
    except Exception as e:
        print(e)
        print(bill_info)
        raise e


def parse_archive(f_path: str):
    archive = ZipFile(f_path)
    for file in archive.namelist():
        r = archive.open(file, "r").read()
        parse_status(r)
