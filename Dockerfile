# -- Base image --
FROM python:3.11-slim as base

# Upgrade pip to its latest release to speed up dependencies installation
RUN pip install --upgrade pip

# Upgrade system packages to install security updates
RUN apt-get update && \
    apt-get -y upgrade && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy all sources
COPY . /app/

# -- Development --
FROM base as development

# Install edx2gift in editable mode along with development dependencies
RUN pip install -e .[dev]
