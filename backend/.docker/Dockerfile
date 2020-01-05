FROM python:3.7.4-slim-stretch

RUN apt update
RUN apt install wget -y

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app

ENTRYPOINT ["python3", "-m", "billparser"]