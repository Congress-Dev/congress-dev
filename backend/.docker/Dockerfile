FROM python:3.13-slim

RUN apt update
RUN apt install wget build-essential -y

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app

ENTRYPOINT ["sh"]