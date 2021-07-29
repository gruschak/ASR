FROM python:3.9

RUN apt-get update
RUN apt-get install -y portaudio19-dev

ADD requirements.txt ./requirements.txt

RUN pip install --upgrade pip && pip install -r requirements.txt

WORKDIR /app
