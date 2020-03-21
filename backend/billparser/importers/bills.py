import os
import sys
import json
import zipfile
from billparser.run_through import parse_archive, ensure_congress


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
    bill_versions = json.load(open(sys.argv[1], "rt"))
    for rp in bill_versions:
        print("=" * 5)
        print(rp.get("title"))
        zip_file_path = "bills/" + download_path(rp.get("url"))
        ensure_congress(rp.get("congress", 116))
        parse_archive(zip_file_path)
