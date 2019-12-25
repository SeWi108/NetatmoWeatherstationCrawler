FROM python:3.7.3-stretch

COPY requirements.txt  /tmp/
RUN pip3 install -r /tmp/requirements.txt

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

RUN mkdir log
RUN mkdir src

COPY src/config.ini src
COPY src/databaseConnector.py src
COPY src/netatmoClient.py src
COPY src/main.py src
COPY src/models.py src
COPY src/crawler.py src

WORKDIR ./src

CMD [ "python3", "-u", "main.py" ]
