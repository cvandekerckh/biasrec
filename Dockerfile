FROM python:3.9.9-slim

RUN adduser --disabled-password biasrecuser
WORKDIR /home/biasrecuser

ENV PATH="/home/biasrecuser/.local/bin:$PATH" \
    _PIP_VERSION="20.2.2"

RUN apt-get update \
      && apt-get install -q -y --no-install-recommends \
      git \
      libboost-dev \
      gcc \
      && apt-get clean \
      && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade \
      pip==${_PIP_VERSION}

ENV FLASK_APP microapp.py

COPY .env .env
COPY app app
COPY app.db app.db
COPY bd_test.csv bd_test.csv
COPY boot_develop.sh boot_develop.sh
COPY config.py config.py
COPY microapp.py microapp.py 
COPY migrations migrations
COPY Pipfile Pipfile
COPY Pipfile.lock Pipfile.lock
COPY Users.csv Users.csv

RUN chown -R biasrecuser:biasrecuser ./

USER biasrecuser
RUN pip install --user pipenv
RUN pipenv install --system --deploy --ignore-pipfile

EXPOSE 80
