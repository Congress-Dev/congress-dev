![congress dot dev](https://github.com/mustyoshi/congress-dev/raw/master/.github/banner.png "Congress.dev")
[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/made-with-typescript.svg)](https://forthebadge.com) [![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)

---

## Setup


### Ubuntu
```
sudo apt-get update
sudo apt install libpq-dev python3-dev python3.13-venv build-essential gcc gfortran libc6 libxml2-dev libxslt-dev
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
curl -fsSL https://get.pnpm.io/install.sh | sh -x

cd backend/
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt -r requirements-fastapi.txt -r requirements-test.txt
python3 setup.py develop

cd ../hillstack
cp .env.example .env
pnpm install
```

### Docker

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
chmod +x ./scripts/start_local.sh
sh ./scripts/start_local.sh
```

### Loading the database
From the backend folder, you will need to tell it to parse some files before you can view them. importers.releases will load 1 release point from the US Code website. ~10MB compressed and put it into the database ~500MB in the db.

```bash
docker exec -it docker_parser_api bash

python3 -m congress_parser.importers.releases
python3 -m congress_parser.importers.bills

```
---

## Contributing
Please note we have a code of conduct, please follow it in all your interactions with the project.