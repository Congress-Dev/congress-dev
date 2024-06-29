import os
import sys
import json
import zipfile
from billparser.appropriations.parser import parse_bill_for_appropriations
from billparser.db.models import LegislationVersion
import requests
import argparse
from datetime import datetime
from billparser.run_through import parse_archives, ensure_congress

parser = argparse.ArgumentParser(description="Reprocess")
parser.add_argument("--bill", type=str, help="Which bill you want to reprocess")

PATH_TEMPLATE = "https://www.govinfo.gov/bulkdata/BILLS/{congress}/{session}/{chamber}/BILLS-{congress}-{session}-{chamber}.zip"


def download_path(url: str):
    os.makedirs("bills", exist_ok=True)
    output_name = url.split("/")[-1]
    if os.path.exists(f"bills/{output_name}"):
        return f"bills/{output_name}"
    res = requests.head(url)
    if res.status_code == 404:
        return None
    os.system(f"wget {url} --output-document bills/{output_name}")
    return f"bills/{output_name}"


def calculate_congress_from_year() -> int:
    current_year = datetime.now().year
    congress = ((current_year - 2001) // 2) + 107
    return congress


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

    # After we've downloaded the bills, we can parse them for appropriation
    legis_obj: LegislationVersion = None
    for legis_obj in legis_objs:
        try:
            parse_bill_for_appropriations(legis_obj.legislation_version_id)
        except Exception as e:
            print(e)

