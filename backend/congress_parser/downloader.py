import os


def download():
    """
    Currently hardcoded for just the first session of the 116 congress
    """
    os.makedirs("bills/116", exist_ok=True)
    os.system(
        "wget https://www.govinfo.gov/bulkdata/BILLS/116/1/s/BILLS-116-1-s.zip --output-document bills/116/s_1.zip"
    )
    os.system(
        "wget https://www.govinfo.gov/bulkdata/BILLS/116/1/hr/BILLS-116-1-hr.zip --output-document bills/116/hr_1.zip"
    )


if __name__ == "__main__":
    download()
