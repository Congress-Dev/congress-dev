"""
Congressional Record importer.

Downloads and parses daily Congressional Record PDFs from govinfo.gov.

PDF URL pattern:
    https://www.govinfo.gov/content/pkg/CREC-{year}-{month:02d}-{day:02d}/pdf/CREC-{year}-{month:02d}-{day:02d}.pdf

The importer:
    1. Iterates through dates in the current Congress (119th, starting Jan 2025)
    2. Downloads daily PDF
    3. Extracts text and splits by section (Senate, House, Extensions, Daily Digest)
    4. Identifies speakers and resolves them to legislator bioguide IDs
    5. Extracts bill references from speech text
    6. Stores everything in the crec_* tables

Usage:
    python -m congress_parser.importers.congressional_record
"""

from datetime import datetime, date, timedelta
import io
import logging
import re
import requests

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
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

PDF_URL = "https://www.govinfo.gov/content/pkg/CREC-{year}-{month:02d}-{day:02d}/pdf/CREC-{year}-{month:02d}-{day:02d}.pdf"

# Section header patterns in the PDF
SECTION_HEADERS = {
    re.compile(r"^\s*SENATE\s*$", re.MULTILINE): CRECSection.Senate,
    re.compile(r"^\s*HOUSE OF REPRESENTATIVES\s*$", re.MULTILINE): CRECSection.House,
    re.compile(r"^\s*EXTENSIONS OF REMARKS\s*$", re.MULTILINE): CRECSection.Extensions,
    re.compile(r"^\s*DAILY DIGEST\s*$", re.MULTILINE): CRECSection.DailyDigest,
}

# Heading pattern: all-caps line that marks a new topic/granule
HEADING_PATTERN = re.compile(r"^([A-Z][A-Z0-9 \-\'\.,]{4,})$")


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


def extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract plain text from PDF bytes using pdfminer."""
    output = io.StringIO()
    laparams = LAParams(line_margin=0.5, word_margin=0.1)
    extract_text_to_fp(io.BytesIO(pdf_bytes), output, laparams=laparams, output_type="text", codec="utf-8")
    return output.getvalue()


def split_pdf_into_sections(text: str) -> list:
    """
    Split raw PDF text into sections (Senate, House, Extensions, DailyDigest).
    Returns a list of dicts: {section: CRECSection, text: str}
    """
    # Find all section header positions
    positions = []
    for pattern, section in SECTION_HEADERS.items():
        for m in pattern.finditer(text):
            positions.append((m.start(), section, m.end()))

    if not positions:
        return [{"section": CRECSection.Senate, "text": text}]

    positions.sort(key=lambda x: x[0])
    sections = []
    for i, (start, section, end) in enumerate(positions):
        section_text = text[end: positions[i + 1][0] if i + 1 < len(positions) else len(text)]
        sections.append({"section": section, "text": section_text.strip()})

    return sections


def split_section_into_granules(section_text: str, section: CRECSection) -> list:
    """
    Split a section's text into granules (topics) based on all-caps headings.
    Returns a list of dicts: {title: str, text: str}
    """
    lines = section_text.split("\n")
    granules = []
    current_title = "General"
    current_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            current_lines.append(line)
            continue
        if HEADING_PATTERN.match(stripped) and len(stripped) > 5:
            if current_lines and any(l.strip() for l in current_lines):
                granules.append({"title": current_title, "text": "\n".join(current_lines).strip()})
            current_title = stripped.title()
            current_lines = []
        else:
            current_lines.append(line)

    if current_lines and any(l.strip() for l in current_lines):
        granules.append({"title": current_title, "text": "\n".join(current_lines).strip()})

    return granules if granules else [{"title": "General", "text": section_text}]


def parse_granule_speeches(granule_text: str) -> list:
    """
    Parse a granule's text into speech segments by speaker.
    Returns a list of dicts: {speaker_raw, content_text, order_number}
    """
    speeches = []
    current_speaker = ""
    current_lines = []
    order = 0

    for line in granule_text.split("\n"):
        text = unidecode(line.strip())
        if not text:
            if current_lines:
                current_lines.append("")
            continue

        speaker = extract_speaker_name(text)
        if speaker and speaker != current_speaker:
            if current_lines:
                full_text = "\n".join(current_lines).strip()
                if full_text:
                    speeches.append({
                        "speaker_raw": current_speaker,
                        "content_text": full_text,
                        "order_number": order,
                    })
                    order += 1
            current_speaker = speaker
            current_lines = [text]
        else:
            current_lines.append(text)

    if current_lines:
        full_text = "\n".join(current_lines).strip()
        if full_text:
            speeches.append({
                "speaker_raw": current_speaker,
                "content_text": full_text,
                "order_number": order,
            })

    return speeches


def import_daily_record(issue_date: date, session, congress_id: int):
    """Import a single day's Congressional Record from the PDF."""
    package_id = f"CREC-{issue_date.isoformat()}"

    existing = session.query(CRECIssue).filter(
        CRECIssue.package_id == package_id
    ).first()
    if existing:
        logger.info(f"Skipping {package_id} - already imported")
        return

    url = PDF_URL.format(
        year=issue_date.year,
        month=issue_date.month,
        day=issue_date.day,
    )

    logger.info(f"Downloading {url}")
    try:
        resp = requests.get(url, timeout=120)
    except requests.RequestException as e:
        logger.warning(f"Failed to download {url}: {e}")
        return

    if resp.status_code == 404:
        logger.debug(f"No record for {issue_date} (404)")
        return
    if resp.status_code != 200:
        logger.warning(f"Unexpected status {resp.status_code} for {url}")
        return

    logger.info(f"Extracting text from {package_id} PDF ({len(resp.content)} bytes)")
    try:
        full_text = extract_pdf_text(resp.content)
    except Exception as e:
        logger.warning(f"Failed to extract PDF text for {package_id}: {e}")
        return

    issue = CRECIssue(
        issue_date=issue_date,
        congress_id=congress_id,
        package_id=package_id,
    )
    session.add(issue)
    session.flush()

    speaker_cache = {}
    granule_order = 0

    sections = split_pdf_into_sections(full_text)
    for sec in sections:
        section = sec["section"]
        granules = split_section_into_granules(sec["text"], section)

        for gran in granules:
            granule = CRECGranule(
                crec_issue_id=issue.crec_issue_id,
                granule_id=f"{package_id}/{section.value}/{granule_order}",
                section=section,
                title=gran["title"],
                order_number=granule_order,
            )
            session.add(granule)
            session.flush()
            granule_order += 1

            speech_segments = parse_granule_speeches(gran["text"])
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
    return True


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
