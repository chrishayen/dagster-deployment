#!/bin/bash
set -e

export POSTGRESQL_HOSTNAME=${POSTGRESQL_HOSTNAME:-postgres}
export POSTGRESQL_USERNAME=${POSTGRESQL_USERNAME:-dagster}
export POSTGRESQL_PASSWORD=${POSTGRESQL_PASSWORD:-dagster}
export POSTGRESQL_DB=${POSTGRESQL_DB:-dagster}

# Build CELERY_BROKER_URL from APP_CONFIG_BROKER_CONNECTION_* environment variables
CONNECTION_URL=${APP_CONFIG_BROKER_CONNECTION_URL:-https://rabbitmq:5672/}
LOGIN=${APP_CONFIG_BROKER_CONNECTION_LOGIN:-dagster}
PASSWORD=${APP_CONFIG_BROKER_CONNECTION_PASSWORD:-dagster}

# Parse host and port from connection URL (format: https://host:port/)
CONNECTION_URL=${CONNECTION_URL%/}  # Remove trailing slash
if [[ $CONNECTION_URL =~ ://(.+):([0-9]+)$ ]]; then
    HOST="${BASH_REMATCH[1]}"
    PORT="${BASH_REMATCH[2]}"
else
    HOST="rabbitmq"
    PORT="5672"
fi

# Construct pyamqp URL for Celery
export CELERY_BROKER_URL="pyamqp://${LOGIN}:${PASSWORD}@${HOST}:${PORT}//"
export CELERY_BACKEND_URL=${CELERY_BACKEND_URL:-rpc://}
export PYTHONPATH=/app/code:$PYTHONPATH

dagster-celery worker start -A dagster_celery.app -y /workspace.yaml
