FROM python:3.10.12-slim-buster

# Setup pipx and poetry
ENV POETRY_VERSION=1.3.2
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
ENV POETRY_CACHE_DIR=/opt/.cache

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Set up a volume for data persistence
VOLUME /duckdb_data

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

RUN apt update && apt install -y apt-utils vim gcc g++ python3-dev openssl \ 
    libxml2-dev libxslt1-dev zlib1g-dev libffi-dev libssl-dev libc-dev libkrb5-dev git \
    libcurl4-openssl-dev wget unzip

# Download and extract DuckDB CLI
RUN wget -q https://github.com/duckdb/duckdb/releases/download/v0.3.1/duckdb_cli-linux-amd64.zip \
    && unzip duckdb_cli-linux-amd64.zip \
    && chmod +x duckdb \
    && mv duckdb /usr/local/bin/

# Poetry setup
COPY pyproject.toml /data-engineering-workshop/pyproject.toml
COPY poetry.lock /data-engineering-workshop/poetry.lock
WORKDIR /data-engineering-workshop
RUN poetry config virtualenvs.create false
RUN poetry install --no-root
RUN rm -rf .venv/ || true
COPY . /data-engineering-workshop/
RUN poetry install --no-interaction
