#!/bin/bash

cd /home/mustyoshi/Github/congress-dev/backend
# rm bills/*

cd /home/mustyoshi/Github/congress-dev
TABLE_NAME="us_code_2023"

docker rm congress-bill-parser && 1

docker-compose -f .docker/docker-compose.yml build congress_parser_api

# Import bills first
docker run --name congress-bill-parser --entrypoint "python3" \
 --env db_host=10.0.0.248 --env db_user=parser --env db_pass=parser \
  --env CONGRESS_API_KEY=By7KBbvlbNsDfoBPLxVAaZj3hvm7aQOnwLOhxvOo \
 --env db_table=${TABLE_NAME} --env PARSE_THREADS=16 \
 --env DISCORD_WEBHOOK=https://discord.com/api/webhooks/817897502442913822/M-6FpliQvtba68dSnL6AqviGkRgSZb5Jan0Hte841WrIxmJiWFWoEN5caWSxahf0Ydha \
 -v /home/mustyoshi/Github/congress-dev/backend/bills:/bills \
 congress_parser_api -m billparser.importers.bills

# Run prompts
docker run --name congress-bill-parser --entrypoint "python3" \
 --env db_host=10.0.0.248 --env db_user=parser --env db_pass=parser \
 --env db_table=${TABLE_NAME} \
 --env DISCORD_WEBHOOK=https://discord.com/api/webhooks/817897502442913822/M-6FpliQvtba68dSnL6AqviGkRgSZb5Jan0Hte841WrIxmJiWFWoEN5caWSxahf0Ydha \
 -v /home/mustyoshi/Github/congress-dev/backend/bills:/bills \
 congress_parser_api -m billparser.importers.prompts

# docker run --name congress-bill-parser --entrypoint "python3" \
#  --env db_host=10.0.0.248 --env db_user=parser --env db_pass=parser \
#  --env db_table=${TABLE_NAME} \
#  --env DISCORD_WEBHOOK=https://discord.com/api/webhooks/817897502442913822/M-6FpliQvtba68dSnL6AqviGkRgSZb5Jan0Hte841WrIxmJiWFWoEN5caWSxahf0Ydha \
#  -v /home/mustyoshi/Github/congress-dev/backend/bills:/bills \
#  congress_parser_api -m billparser.importers.bioguide

# Grab sponsors
docker run --name congress-bill-parser --entrypoint "python3" \
 --env db_host=10.0.0.248 --env db_user=parser --env db_pass=parser \
 --env db_table=${TABLE_NAME} \
 --env CONGRESS_API_KEY=${CONGRESS_API_KEY} \
 --env DISCORD_WEBHOOK=https://discord.com/api/webhooks/817897502442913822/M-6FpliQvtba68dSnL6AqviGkRgSZb5Jan0Hte841WrIxmJiWFWoEN5caWSxahf0Ydha \
 -v /home/mustyoshi/Github/congress-dev/backend/bills:/bills \
 congress_parser_api -m billparser.importers.sponsors

# docker run --name congress-bill-parser --entrypoint "python3" \
#  --env db_host=10.0.0.248 --env db_user=parser --env db_pass=parser \
#  --env db_table=${TABLE_NAME} \
#  --env CONGRESS_API_KEY=${CONGRESS_API_KEY} \
#  --env DISCORD_WEBHOOK=https://discord.com/api/webhooks/817897502442913822/M-6FpliQvtba68dSnL6AqviGkRgSZb5Jan0Hte841WrIxmJiWFWoEN5caWSxahf0Ydha \
#  -v /home/mustyoshi/Github/congress-dev/backend/bills:/bills \
#  congress_parser_api -m billparser.importers.releases

# Run action importer
docker run --name congress-bill-parser --entrypoint "python3" \
 --env db_host=10.0.0.248 --env db_user=parser --env db_pass=parser \
 --env db_table=${TABLE_NAME} \
 --env CONGRESS_API_KEY=${CONGRESS_API_KEY} \
 --env DISCORD_WEBHOOK=https://discord.com/api/webhooks/817897502442913822/M-6FpliQvtba68dSnL6AqviGkRgSZb5Jan0Hte841WrIxmJiWFWoEN5caWSxahf0Ydha \
 -v /home/mustyoshi/Github/congress-dev/backend/bills:/bills \
 congress_parser_api -m billparser.importers.actions

docker rm congress-bill-parser && 1

docker run --name congress-bill-cleanup --entrypoint "python3" \
 --env db_host=10.0.0.248 --env db_user=parser --env db_pass=parser \
 --env db_table=${TABLE_NAME} --env PARSE_THREADS=16 \
 --env DISCORD_WEBHOOK=https://discord.com/api/webhooks/817897502442913822/M-6FpliQvtba68dSnL6AqviGkRgSZb5Jan0Hte841WrIxmJiWFWoEN5caWSxahf0Ydha \
  congress_parser_api -m billparser.importers.cleanup

docker rm congress-bill-cleanup && 1
