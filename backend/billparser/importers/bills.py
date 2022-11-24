import os
import sys
import json
import zipfile
import requests
import argparse
from datetime import datetime
from billparser.run_through import parse_archive, ensure_congress

parser = argparse.ArgumentParser(description="Reprocess")
parser.add_argument("--bill", type=str, help="Which bill you want to reprocess")

PATH_TEMPLATE = "https://www.govinfo.gov/bulkdata/BILLS/{congress}/{session}/{chamber}/BILLS-{congress}-{session}-{chamber}.zip"


def download_path(url: str):
    os.makedirs("bills", exist_ok=True)
    output_name = url.split("/")[-1]
    if os.path.exists(f"bills/{output_name}"):
        return output_name
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
            if bill != None:
                parse_archive(
                    zip_file_path,
                    chamber_filter=chamber_lookup[bill.split(" ")[0]],
                    number_filter=bill.split(" ")[1],
                )
            else:
                parse_archive(zip_file_path)
