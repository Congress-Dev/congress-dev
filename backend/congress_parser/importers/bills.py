"""
Bill data downloader and ingestion entry point.

Downloads bulk bill XML ZIP archives from govinfo.gov and feeds them into the
parsing pipeline (run_through.parse_archives). For each Congress, there are up
to 4 ZIPs: 2 sessions x 2 chambers (House + Senate).

URL pattern:
    https://www.govinfo.gov/bulkdata/BILLS/{congress}/{session}/{chamber}/
        BILLS-{congress}-{session}-{chamber}.zip

Usage:
    python -m congress_parser.importers.bills              # Import all bills for current Congress
    python -m congress_parser.importers.bills "HR 1234"    # Import a specific bill
"""

import os
import sys
import json
import zipfile
from congress_parser.appropriations.parser import parse_bill_for_appropriations
from congress_db.models import LegislationVersion
import requests
import argparse
from datetime import datetime
from congress_parser.run_through import parse_archives, ensure_congress

webhook_url = os.environ.get("DISCORD_WEBHOOK", None)

parser = argparse.ArgumentParser(description="Reprocess")
parser.add_argument("--bill", type=str, help="Which bill you want to reprocess")

PATH_TEMPLATE = "https://www.govinfo.gov/bulkdata/BILLS/{congress}/{session}/{chamber}/BILLS-{congress}-{session}-{chamber}.zip"


def download_path(url: str, *, dir_name: str = "bills"):
    os.makedirs(dir_name, exist_ok=True)
    output_name = url.split("/")[-1]
    if os.path.exists(f"{dir_name}/{output_name}"):
        return f"{dir_name}/{output_name}"
    res = requests.head(url)
    if res.status_code == 404:
        return None
    os.system(f"wget {url} --output-document {dir_name}/{output_name}")
    return f"{dir_name}/{output_name}"


def calculate_congress_from_year() -> int:
    """
    Derives the current Congress number from the calendar year.
    Congress 107 started in 2001; a new Congress convenes every 2 years.
    e.g. 2025 → ((2025-2001)//2)+107 = 119th Congress
    """
    current_year = datetime.now().year
    congress = ((current_year - 2001) // 2) + 107
    return congress

def send_message(text):
    if webhook_url is not None:
        import requests

        requests.post(webhook_url, json={"content": text})

if __name__ == "__main__":
    """
    Downloads the latest zip from the bulk data repo
    will then parse it out and attempt to load each version into
    the database
    """
    chamber_lookup = {"HR": "House", "S": "Senate"}
    bill = None
    if len(sys.argv) > 1:
        bill = sys.argv[1]

    congress = calculate_congress_from_year()
    ensure_congress(congress)

    legis_objs = []
    zip_paths = []
    for session in [1, 2]:
        for chamber in ["hr", "s"]:
            print("=" * 5)
            print(f"{congress}: {session} - {chamber}")
            zip_file_path = download_path(
                PATH_TEMPLATE.format(
                    congress=congress, session=session, chamber=chamber
                )
            )
            if zip_file_path is None:
                print("Could not find archive")
                continue
            zip_paths.append(zip_file_path)

    if bill != None:
        legis_objs = parse_archives(
            zip_paths,
            chamber_filter=chamber_lookup[bill.split(" ")[0]],
            number_filter=bill.split(" ")[1],
        )
    else:
        legis_objs = parse_archives(zip_paths)

    send_message(
        f"Added {len(legis_objs)} new bills today"
    )