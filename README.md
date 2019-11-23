# Congress.Dev Mono Repo

# Instructions

```bash
docker-compose .docker/docker-compose.yml build
docker-compose .docker/docker-compose.yml up -d
```

## Loading the database
From the backend folder, you will need to tell it to parse some files before you can view them. importers.releases will load 3 release points from the US Code website. ~10MB compressed and put it into the database ~500MB in the db.
run_through will load the first 100 bills from the senate and the first 100 bills from the house (limited to 100 for speed), you can change it on line 671

```bash
docker exec -it docker_parser_api bash

python3 -m billparser.importers.releases rp.json
python3 -m billparser.run_through

```

# Helpful Resources
https://designsystem.digital.gov/design-tokens/color/system-tokens/