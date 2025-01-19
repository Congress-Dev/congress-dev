
from datetime import datetime
from joblib import Parallel, delayed
from lxml import html
import os
import re
import requests
from sqlalchemy import func
import zipfile

from billparser.db.handler import import_title, get_number, Session
from billparser.db.models import USCRelease, Version


THREADS = int(os.environ.get("PARSE_THREADS", -1))
DOWNLOAD_BASE = "https://uscode.house.gov/download/{}"
RELEASE_POINTS = "https://uscode.house.gov/download/priorreleasepoints.htm"

def download_path(url: str):
    os.makedirs("usc", exist_ok=True)
    output_name = url.split("@")[-1]
    if os.path.exists(f"usc/{output_name}"):
        return output_name
    os.system(f"wget {url} --output-document usc/{output_name}")
    return output_name


if __name__ == "__main__":
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

