docker-compose -f .docker/docker-compose.yml -f .docker/docker-compose.prod.yml build
docker-compose -f .docker/docker-compose.yml -f .docker/docker-compose.prod.yml down
docker-compose -f .docker/docker-compose.yml -f .docker/docker-compose.prod.yml up -d