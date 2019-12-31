from billparser.db.handler import import_title, get_number, Session
from billparser.db.models import USCRelease, Version
from sqlalchemy import func
import os
import sys
import json
import zipfile
from datetime import datetime
from joblib import Parallel, delayed

THREADS = int(os.environ.get("PARSE_THREADS", -1))


def download_path(url: str):
    os.makedirs("usc", exist_ok=True)
    output_name = url.split("@")[-1]
    if os.path.exists(f"usc/{output_name}"):
        return output_name
    os.system(f"wget {url} --output-document usc/{output_name}")
    return output_name


if __name__ == "__main__":
    release_points = json.load(open(sys.argv[1], "rt"))
    session = Session()
    for rp in release_points:
        print("=" * 5)
        print(rp.get("short_title"))
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
                for file in files
            )

