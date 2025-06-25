#!/usr/bin/env bash

cd daemon
poetry run dagster-daemon run -w /workspace.yaml