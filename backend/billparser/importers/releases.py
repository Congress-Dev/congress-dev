from billparser.db.handler import import_title, get_number
import os
import sys
import json
import zipfile


def download_path(url: str):
    os.makedirs("usc", exist_ok=True)
    output_name = url.split("@")[-1]
    if os.path.exists(f"usc/{output_name}"):
        return output_name
    os.system(f"wget {url} --output-document usc/{output_name}")
    return output_name


if __name__ == "__main__":
    release_points = json.load(open(sys.argv[1], "rt"))
    for rp in release_points:
        print("=" * 5)
        print(rp.get("title"))
        zip_file_path = download_path(rp.get("url"))
        with zipfile.ZipFile(f"usc/{zip_file_path}") as zip_file:
            files = zip_file.namelist()

            files = sorted(
                files, key=lambda x: get_number(x.split(".")[0].replace("usc", ""))
            )
            for file in files:
                import_title(
                    zip_file.open(file),
                    file.split(".")[0].replace("usc", ""),
                    rp.get("title"),
                )

