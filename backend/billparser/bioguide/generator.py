import requests
import json
import zipfile
import io
import os
from genson import SchemaBuilder
if __name__ == "__main__":
    BULK_BIOGUIDE_URL = "https://bioguide.congress.gov/bioguide/data/BioguideProfiles.zip"
    r = requests.get(BULK_BIOGUIDE_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    builder = SchemaBuilder()
    for filename in z.namelist():
        if filename.endswith(".json"):
            builder.add_object(json.loads(z.read(filename)))
    schema = builder.to_schema()
    json.dump(schema, open("schema.json", "w"), indent=2)
    os.system("datamodel-codegen  --input schema.json --input-file-type jsonschema --output bioguide.py")