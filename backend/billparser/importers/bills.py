import os
import sys
import json
import zipfile
import argparse

from billparser.run_through import parse_archive, ensure_congress

parser = argparse.ArgumentParser(description="Reprocess")
parser.add_argument("--bill", type=str, help="Which bill you want to reprocess")



def download_path(url: str):
    os.makedirs("bills", exist_ok=True)
    output_name = url.split("/")[-1]
    if os.path.exists(f"bills/{output_name}"):
        return output_name
    os.system(f"wget {url} --output-document bills/{output_name}")
    return output_name


if __name__ == "__main__":
    """
    Downloads the latest zip from the bulk data repo
    will then parse it out and attempt to load each version into
    the database
    """
    chamber_lookup = {"HR": "House", "S": "Senate"}
    bill_versions = json.load(open(sys.argv[1], "rt"))
    bill = None
    if len(sys.argv) > 2:
        bill = sys.argv[2]
    for rp in bill_versions:
        print("=" * 5)
        print(rp.get("title"))
        zip_file_path = "bills/" + download_path(rp.get("url"))
        ensure_congress(rp.get("congress", 117))
        if bill != None:
            parse_archive(
                zip_file_path,
                chamber_filter=chamber_lookup[bill.split(" ")[0]],
                number_filter=bill.split(" ")[1],
            )
        else:
            parse_archive(zip_file_path)
