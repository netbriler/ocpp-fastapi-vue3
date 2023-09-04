FROM python:3.11.3-slim-bullseye

RUN apt-get update && apt-get install -y build-essential curl

RUN mkdir -p /usr/src/csms/backend
RUN mkdir -p /usr/src/csms/frontend

WORKDIR /usr/src/csms

COPY backend/src /usr/src/csms/backend
COPY frontend /usr/src/csms/frontend

ENV PYTHONPATH=/usr/src/csms/backend

RUN pip install --no-cache-dir -r /usr/src/csms/backend/requirements.txt --upgrade pip

RUN apt-get update && \
    curl -s https://deb.nodesource.com/setup_18.x | bash && apt-get install -y nodejs
RUN curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && \
    apt-get install yarn -y

