FROM mcr.microsoft.com/devcontainers/python:3.12-bookworm

WORKDIR /app

# COPY sources.list /etc/apt/sources.list

# install ngspice
RUN apt-get update && \
    sudo apt-get -y install ngspice && \
    rm -rf /var/lib/apt/lists/*

# intstall my Python modules
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN rm ./requirements.txt
