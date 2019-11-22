FROM python:3.7.4-slim-stretch

RUN apt update
RUN apt install wget -y

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app

<<<<<<< HEAD
ENTRYPOINT ["python3", "-m", "billparser"]
=======
EXPOSE 9090
EXPOSE 80

ENTRYPOINT ["python", "-m", "billparser"]
>>>>>>> Remove bootstrap
