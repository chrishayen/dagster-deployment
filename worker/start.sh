#!/bin/bash
set -e

export POSTGRESQL_HOSTNAME=${POSTGRESQL_HOSTNAME:-postgres}
export POSTGRESQL_USERNAME=${POSTGRESQL_USERNAME:-dagster}
export POSTGRESQL_PASSWORD=${POSTGRESQL_PASSWORD:-dagster}
export POSTGRESQL_DB=${POSTGRESQL_DB:-dagster}
export CELERY_BROKER_URL=${CELERY_BROKER_URL:-pyamqp://dagster:dagster@rabbitmq:5672//}
export CELERY_BACKEND_URL=${CELERY_BACKEND_URL:-rpc://}
export PYTHONPATH=/app/code:$PYTHONPATH

dagster-celery worker start -A dagster_celery.app -y /workspace.yaml
