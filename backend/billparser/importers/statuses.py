import os
from billparser.status_parser import parse_archive

url_format = "https://www.govinfo.gov/bulkdata/BILLSTATUS/{congress}/{prefix}/BILLSTATUS-{congress}-{prefix}.zip"

congresses = [118]

def download_path(url: str):
    os.makedirs("statuses", exist_ok=True)
    output_name = url.split("/")[-1]
    if os.path.exists(f"statuses/{output_name}"):
        return output_name
    os.system(f"wget {url} --output-document statuses/{output_name}")
    return output_name

if __name__ == "__main__":
    for congress in congresses:
        for prefix in ["hr"]:
            url = url_format.format(**{"congress": congress, "prefix": prefix})
            output_name = download_path(url)
            parse_archive(f"statuses/{output_name}")