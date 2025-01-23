import argparse
import html
import os
import zipfile
from datetime import datetime
from billparser.importers.bills import download_path
from joblib import Parallel, delayed
import requests
from sqlalchemy import func
from billparser.db.handler import import_title, get_number, Session
from billparser.db.models import USCRelease, Version

THREADS = int(os.environ.get("PARSE_THREADS", -1))
DOWNLOAD_BASE = "https://uscode.house.gov/download/{}"
RELEASE_POINTS = "https://uscode.house.gov/download/priorreleasepoints.htm"

def main():
    parser = argparse.ArgumentParser(description="Process release points.")
    parser.add_argument('--release-point', type=str, help='URL of the zip file to process a single release point')
    args = parser.parse_args()

    if args.release_point:
        process_single_release_point(args.release_point)
    else:
        process_all_release_points()

def process_single_release_point(url, release = None):
    zip_file_path = download_path(url)
    with zipfile.ZipFile(zip_file_path) as zip_file:
        files = zip_file.namelist()
        files = sorted(files, key=lambda x: get_number(x.split(".")[0].replace("usc", "")))
        Parallel(n_jobs=THREADS, verbose=5, backend="loky")(
            delayed(import_title)(
                zip_file.open(file).read(),
                file.split(".")[0].replace("usc", ""),
                None,  # Assuming title is not needed for single release point
                release   # Assuming release_point.to_dict() is not needed for single release point
            )
            for file in files
        )

def process_all_release_points():
    release_points = []
    response = requests.get(RELEASE_POINTS)
    tree = html.fromstring(response.content)

    for year in range(2022, datetime.now().year, 2):
        search_date = f"12/21/{year}"
        links = tree.xpath(f'//a[contains(text(), "{search_date}")]/@href')

        if len(links) > 0:
            link = links[0].replace('usc-rp', 'xml_uscAll').replace('.htm', '.zip')
            zipPath = DOWNLOAD_BASE.format(link)
            match = re.search(r'@(\d+)-(\d+)\.zip', link)

            release_points.append({
                "date": search_date,
                "short_title": f"Public Law {match.group(1)}-{match.group(2)}",
                "long_title": "",
                "url": zipPath
            })

    session = Session()
    for rp in release_points:
        existing_rp = (
            session.query(USCRelease)
            .filter(
                USCRelease.short_title == rp.get("short_title"),
                func.date(USCRelease.effective_date)
                == datetime.strptime(rp.get("date"), "%m/%d/%Y"),
            )
            .all()
        )
        if len(existing_rp) > 0:
            print("Already in DB - Skipping")
            continue
        new_version = Version(base_id=None)
        session.add(new_version)
        session.commit()
        release_point = USCRelease(
            short_title=rp.get("short_title"),
            effective_date=datetime.strptime(rp.get("date"), "%m/%d/%Y"),
            long_title=rp.get("long_title"),
            version_id=new_version.version_id,
        )
        session.add(release_point)
        session.commit()
        zip_file_path = download_path(rp.get("url"))
        with zipfile.ZipFile(f"usc/{zip_file_path}") as zip_file:
            files = zip_file.namelist()

            files = sorted(
                files, key=lambda x: get_number(x.split(".")[0].replace("usc", ""))
            )
            Parallel(n_jobs=THREADS, verbose=5, backend="multiprocessing")(
                delayed(import_title)(
                    zip_file.open(file).read(),
                    file.split(".")[0].replace("usc", ""),
                    rp.get("title"),
                    release_point.to_dict(),
                )
                for file in files  # if "09" in file
            )

if __name__ == "__main__":
    main()

