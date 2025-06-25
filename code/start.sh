#!/usr/bin/env bash

cd code
poetry run dagster code-server start -h 0.0.0.0 -p 4000 -m main
