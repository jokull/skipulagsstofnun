FROM python:3.9 as requirements-stage

WORKDIR /tmp

# Install system packages for Fiona python package
RUN DEBIAN_FRONTEND=noninteractive apt-get update \
  && apt-get -y install --no-install-recommends gdal-bin libgdal-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# FROM python:3.9

# WORKDIR /code

# COPY --from=requirements-stage /tmp/requirements.txt /code/requirements.txt

# RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# COPY . /code/
