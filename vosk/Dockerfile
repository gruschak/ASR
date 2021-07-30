FROM python:3.9

ADD requirements.txt ./requirements.txt

RUN apt-get update
RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /app
