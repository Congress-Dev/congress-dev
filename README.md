![congress dot dev](https://github.com/mustyoshi/congress-dev/raw/master/.github/banner.png "Congress.dev")
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/uses-js.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)

---

## Setup

### Required Software

#### Docker `>= 19.0`
Docker is a set of platform as a service products that use OS-level virtualization to deliver software in packages called containers.
https://docs.docker.com/install/

#### Docker-Compose `>= 1.24`
Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application's services.
https://docs.docker.com/compose/install/

---

## Usage

**Basic usage** - To start an entirely local copy. This will come with an empty database, you'll have to follow the instructions to populate it (or load the provided backup).
```bash
docker-compose -f .docker/docker-compose.yml up -d
```

**Advance Usage** - If you rename [docker-compose.local-example.yml](./.docker/docker-compose.local-example.yml) to `docker-compose.local.yml` you can run this script to use our API instead of running the database yourself.
```bash
chmod +x ./start_local.sh
sh ./start_local.sh
```

### Loading the database
From the backend folder, you will need to tell it to parse some files before you can view them. importers.releases will load 1 release point from the US Code website. ~10MB compressed and put it into the database ~500MB in the db.
A semi up to date postgres dump is available for [download](https://files.congress.dev/congress_beta.backup)

```bash
docker exec -it docker_parser_api bash

python3 -m billparser.importers.releases rp.json
python3 -m billparser.importers.bills bills.json

```

---

## Contributing
Please note we have a code of conduct, please follow it in all your interactions with the project.