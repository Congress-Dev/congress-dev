# Congress.Dev Mono Repo

# Instructions

```bash
docker-compose .docker/docker-compose.yml build
docker-compose .docker/docker-compose.yml up -d
```

## Loading the database
From the backend folder, you will need to tell it to parse some files before you can view them. importers.releases will load 1 release point from the US Code website. ~10MB compressed and put it into the database ~500MB in the db.
A semi up to date postgres dump is available for [download](https://files.congress.dev/congress_beta.backup)

```bash
docker exec -it docker_parser_api bash

python3 -m billparser.importers.releases rp.json
python3 -m billparser.importers.bills bills.json

```

# Helpful Resources
https://designsystem.digital.gov/design-tokens/color/system-tokens/