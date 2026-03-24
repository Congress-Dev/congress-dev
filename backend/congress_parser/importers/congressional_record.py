"""
Congressional Record importer.

Downloads and parses daily Congressional Record bulk data from govinfo.gov.
Each daily issue is a ZIP containing HTML/XML files organized by section
(Senate, House, Extensions of Remarks, Daily Digest).

Bulk data URL pattern:
    https://www.govinfo.gov/bulkdata/CREC/{year}/{month:02d}/{day:02d}/CREC-{year}-{month:02d}-{day:02d}.zip

The importer:
    1. Iterates through dates in the current Congress (119th, starting Jan 2025)
    2. Downloads daily ZIP packages
    3. Parses HTML/XML granules to extract debate segments
    4. Identifies speakers and resolves them to legislator bioguide IDs
    5. Extracts bill references from speech text
    6. Stores everything in the crec_* tables

Usage:
    python -m congress_parser.importers.congressional_record
"""

from datetime import datetime, date, timedelta
import io
import logging
import os
import re
import requests
import tempfile
import zipfile

from lxml import etree, html
from unidecode import unidecode

from congress_db.session import Session
from congress_db.models import (
    CRECIssue,
    CRECGranule,
    CRECSpeech,
    CRECBillReference,
    CRECSection,
    Congress,
    Legislator,
    Legislation,
    LegislationChamber,
    LegislationType,
)
from congress_parser.utils.cite_parser import extract_bill_references

logger = logging.getLogger(__name__)

BULK_DATA_URL = "https://www.govinfo.gov/bulkdata/CREC/{year}/{month:02d}/{day:02d}/CREC-{year}-{month:02d}-{day:02d}.zip"


def calculate_congress_from_year() -> int:
    current_year = datetime.now().year
    return ((current_year - 2001) // 2) + 107


def get_congress_start_date(congress_number: int) -> date:
    """Get the start date for a given Congress number."""
    start_year = 2001 + (congress_number - 107) * 2
    return date(start_year, 1, 3)


def map_section(filename: str) -> CRECSection:
    """Map a CREC filename or path to a CRECSection enum."""
    lower = filename.lower()
    if "/senate/" in lower or "senate" in lower:
        return CRECSection.Senate
    elif "/house/" in lower or "house" in lower:
        return CRECSection.House
    elif "/extensions/" in lower or "extension" in lower:
        return CRECSection.Extensions
    elif "/dailydigest/" in lower or "digest" in lower:
        return CRECSection.DailyDigest
    return CRECSection.Senate


SPEAKER_PATTERN = re.compile(
    r"^(?:Mr|Mrs|Ms|Miss|Madam|The)\.\s+([A-Z][A-Z\-\']+(?:\s+[A-Z][A-Z\-\']+)*)",
    re.IGNORECASE,
)

SPEAKER_PREFIX_PATTERN = re.compile(
    r"^(?:Mr|Mrs|Ms|Miss)\.\s+(?:Speaker|President|SPEAKER|PRESIDENT)?\s*[,.]?\s*(?:Mr|Mrs|Ms|Miss)\.\s+([A-Z][A-Z\-\']+)",
    re.IGNORECASE,
)


def extract_speaker_name(text: str) -> str:
    """Extract speaker last name from a speech paragraph."""
    text = text.strip()
    match = SPEAKER_PREFIX_PATTERN.match(text)
    if match:
        return match.group(1).upper()
    match = SPEAKER_PATTERN.match(text)
    if match:
        name = match.group(1).upper()
        if name not in ("SPEAKER", "PRESIDENT", "CHAIR", "CHAIRMAN", "CHAIRWOMAN"):
            return name
    return ""


def resolve_speaker(speaker_name: str, chamber: CRECSection, session) -> str:
    """
    Resolve a raw speaker last name to a legislator bioguide_id.
    Uses chamber to disambiguate between House and Senate members.
    """
    if not speaker_name:
        return None

    from congress_db.models import LegislatorJob

    job = None
    if chamber == CRECSection.Senate:
        job = LegislatorJob.Senator
    elif chamber == CRECSection.House:
        job = LegislatorJob.Representative

    query = session.query(Legislator).filter(
        Legislator.last_name == speaker_name.title()
    )
    if job:
        query = query.filter(Legislator.job == job)

    legislators = query.all()
    if len(legislators) == 1:
        return legislators[0].bioguide_id
    elif len(legislators) > 1:
        current_congress = calculate_congress_from_year()
        for leg in legislators:
            if leg.congress_id and current_congress in leg.congress_id:
                return leg.bioguide_id
        return legislators[0].bioguide_id

    return None


def resolve_bill_reference(ref: dict, congress_id: int, session) -> int:
    """Resolve a bill reference dict to a legislation_id, or None."""
    chamber_map = {
        "House": LegislationChamber.House,
        "Senate": LegislationChamber.Senate,
    }
    type_map = {
        "Bill": LegislationType.Bill,
        "Resolution": LegislationType.Res,
        "Joint Resolution": LegislationType.JRes,
        "Continuing Resolution": LegislationType.CRes,
    }

    chamber = chamber_map.get(ref["chamber"])
    leg_type = type_map.get(ref["legislation_type"])

    if not chamber or not leg_type:
        return None

    legislation = (
        session.query(Legislation)
        .filter(
            Legislation.chamber == chamber,
            Legislation.number == ref["number"],
            Legislation.legislation_type == leg_type,
            Legislation.congress_id == congress_id,
        )
        .first()
    )
    return legislation.legislation_id if legislation else None


def parse_htm_content(content: str) -> list:
    """
    Parse an HTML granule file and extract speech segments.
    Returns a list of dicts: {speaker_raw, content_text, order_number}
    """
    try:
        doc = html.fromstring(content)
    except Exception:
        return []

    speeches = []
    current_speaker = ""
    current_paragraphs = []
    order = 0

    paragraphs = doc.xpath("//body//p") or doc.xpath("//p")
    if not paragraphs:
        text = doc.text_content().strip()
        if text:
            speeches.append({
                "speaker_raw": "",
                "content_text": text,
                "order_number": 0,
            })
        return speeches

    for p in paragraphs:
        text = p.text_content().strip()
        if not text:
            continue

        text = unidecode(text)
        speaker = extract_speaker_name(text)

        if speaker and speaker != current_speaker:
            if current_paragraphs:
                full_text = "\n".join(current_paragraphs)
                speeches.append({
                    "speaker_raw": current_speaker,
                    "content_text": full_text,
                    "order_number": order,
                })
                order += 1
            current_speaker = speaker
            current_paragraphs = [text]
        else:
            current_paragraphs.append(text)

    if current_paragraphs:
        full_text = "\n".join(current_paragraphs)
        speeches.append({
            "speaker_raw": current_speaker,
            "content_text": full_text,
            "order_number": order,
        })

    return speeches


def parse_mods_xml(mods_content: str) -> dict:
    """
    Parse the MODS XML metadata file for a daily CREC package.
    Returns a dict of granule_id -> {title, section, page_start, page_end}.
    """
    try:
        root = etree.fromstring(mods_content)
    except Exception:
        return {}

    ns = {"mods": "http://www.loc.gov/mods/v3"}
    granules = {}

    for related in root.findall(".//mods:relatedItem[@type='constituent']", ns):
        identifier_el = related.find("mods:identifier[@type='preferred citation']", ns)
        title_el = related.find("mods:titleInfo/mods:title", ns)

        if identifier_el is None:
            continue

        granule_id = identifier_el.text.strip() if identifier_el.text else None
        title = title_el.text.strip() if title_el is not None and title_el.text else ""

        page_start = None
        page_end = None
        extent_el = related.find("mods:part/mods:extent", ns)
        if extent_el is not None:
            start_el = extent_el.find("mods:start", ns)
            end_el = extent_el.find("mods:end", ns)
            if start_el is not None and start_el.text:
                page_start = start_el.text.strip()
            if end_el is not None and end_el.text:
                page_end = end_el.text.strip()

        if granule_id:
            granules[granule_id] = {
                "title": title,
                "page_start": page_start,
                "page_end": page_end,
            }

    return granules


def import_daily_record(issue_date: date, session, congress_id: int):
    """Import a single day's Congressional Record."""
    package_id = f"CREC-{issue_date.isoformat()}"

    existing = session.query(CRECIssue).filter(
        CRECIssue.package_id == package_id
    ).first()
    if existing:
        logger.info(f"Skipping {package_id} - already imported")
        return

    url = BULK_DATA_URL.format(
        year=issue_date.year,
        month=issue_date.month,
        day=issue_date.day,
    )

    logger.info(f"Downloading {url}")
    try:
        resp = requests.get(url, timeout=60)
    except requests.RequestException as e:
        logger.warning(f"Failed to download {url}: {e}")
        return

    if resp.status_code == 404:
        logger.debug(f"No record for {issue_date} (404)")
        return
    if resp.status_code != 200:
        logger.warning(f"Unexpected status {resp.status_code} for {url}")
        return

    issue = CRECIssue(
        issue_date=issue_date,
        congress_id=congress_id,
        package_id=package_id,
    )
    session.add(issue)
    session.flush()

    try:
        zf = zipfile.ZipFile(io.BytesIO(resp.content))
    except zipfile.BadZipFile:
        logger.warning(f"Bad ZIP file for {package_id}")
        session.rollback()
        return

    mods_metadata = {}
    for name in zf.namelist():
        if name.endswith("mods.xml"):
            try:
                mods_content = zf.read(name)
                mods_metadata = parse_mods_xml(mods_content)
            except Exception as e:
                logger.warning(f"Failed to parse MODS {name}: {e}")
            break

    htm_files = sorted([
        n for n in zf.namelist()
        if n.endswith(".htm") or n.endswith(".html")
    ])

    speaker_cache = {}
    granule_order = 0

    for htm_file in htm_files:
        basename = os.path.splitext(os.path.basename(htm_file))[0]
        section = map_section(htm_file)

        meta = mods_metadata.get(basename, {})
        title = meta.get("title", basename)
        page_start = meta.get("page_start")
        page_end = meta.get("page_end")

        granule = CRECGranule(
            crec_issue_id=issue.crec_issue_id,
            granule_id=f"{package_id}/{basename}",
            section=section,
            title=title,
            page_start=page_start,
            page_end=page_end,
            order_number=granule_order,
        )
        session.add(granule)
        session.flush()
        granule_order += 1

        try:
            content = zf.read(htm_file).decode("utf-8", errors="replace")
        except Exception as e:
            logger.warning(f"Failed to read {htm_file}: {e}")
            continue

        speech_segments = parse_htm_content(content)

        for seg in speech_segments:
            speaker_raw = seg["speaker_raw"]

            if speaker_raw in speaker_cache:
                bioguide_id = speaker_cache[speaker_raw]
            else:
                bioguide_id = resolve_speaker(speaker_raw, section, session)
                speaker_cache[speaker_raw] = bioguide_id

            content_text = seg["content_text"]
            word_count = len(content_text.split())

            speech = CRECSpeech(
                crec_granule_id=granule.crec_granule_id,
                speaker_raw=speaker_raw or None,
                legislator_bioguide_id=bioguide_id,
                order_number=seg["order_number"],
                content_text=content_text,
                word_count=word_count,
            )
            session.add(speech)
            session.flush()

            bill_refs = extract_bill_references(content_text)
            seen_refs = set()
            for ref in bill_refs:
                ref_key = (ref["chamber"], ref["number"], ref["legislation_type"])
                if ref_key in seen_refs:
                    continue
                seen_refs.add(ref_key)

                legislation_id = resolve_bill_reference(ref, congress_id, session)

                bill_reference = CRECBillReference(
                    crec_speech_id=speech.crec_speech_id,
                    legislation_id=legislation_id,
                    cite_text=ref["cite_text"],
                    cite_type=ref["cite_type"],
                    start_offset=ref["start"],
                    end_offset=ref["end"],
                )
                session.add(bill_reference)

    session.commit()
    logger.info(f"Imported {package_id}: {granule_order} granules")


def run_import(start_date: date = None, end_date: date = None):
    """Run the Congressional Record import for a date range."""
    db = Session()

    congress_number = calculate_congress_from_year()
    congress = db.query(Congress).filter(
        Congress.session_number == congress_number
    ).first()

    if not congress:
        logger.error(f"Congress {congress_number} not found in database")
        return

    congress_id = congress.congress_id

    if start_date is None:
        latest = db.query(CRECIssue).order_by(
            CRECIssue.issue_date.desc()
        ).first()
        if latest:
            start_date = latest.issue_date + timedelta(days=1)
        else:
            start_date = get_congress_start_date(congress_number)

    if end_date is None:
        end_date = date.today()

    logger.info(f"Importing Congressional Record from {start_date} to {end_date}")

    current = start_date
    while current <= end_date:
        if current.weekday() < 5:
            try:
                import_daily_record(current, db, congress_id)
            except Exception as e:
                logger.error(f"Error importing {current}: {e}", exc_info=True)
                db.rollback()
        current += timedelta(days=1)

    db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_import()
