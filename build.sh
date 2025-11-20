#!/usr/bin/env bash

docker build --build-arg DAGSTER_APP=code --tag dagster-code-server .
docker build --build-arg DAGSTER_APP=daemon --tag dagster-daemon .
docker build --build-arg DAGSTER_APP=web --tag dagster-webserver .
docker build -f Dockerfile.worker --tag dagster-worker .