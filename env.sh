#!/bin/bash
# Start dagster-celery worker locally with constructed URLs

# PostgreSQL config (defaults match docker-compose)
DAGSTER_PG_USER="${DAGSTER_PG_USER:-dagster}"
DAGSTER_PG_PASSWORD="${DAGSTER_PG_PASSWORD:-dagster}"
DAGSTER_PG_HOST="${DAGSTER_PG_HOST:-localhost}"
DAGSTER_PG_PORT="${DAGSTER_PG_PORT:-5432}"
DAGSTER_PG_DB="${DAGSTER_PG_DB:-dagster}"

# RabbitMQ config (defaults match docker-compose)
RABBITMQ_USER="${RABBITMQ_USER:-guest}"
RABBITMQ_PASSWORD="${RABBITMQ_PASSWORD:-guest}"
RABBITMQ_HOST="${RABBITMQ_HOST:-localhost}"
RABBITMQ_PORT="${RABBITMQ_PORT:-5672}"

# Construct URLs
export CELERY_BROKER_URL="amqp://${RABBITMQ_USER}:${RABBITMQ_PASSWORD}@${RABBITMQ_HOST}:${RABBITMQ_PORT}//"
export CELERY_RESULT_BACKEND="db+postgresql://${DAGSTER_PG_USER}:${DAGSTER_PG_PASSWORD}@${DAGSTER_PG_HOST}:${DAGSTER_PG_PORT}/${DAGSTER_PG_DB}"

echo "CELERY_BROKER_URL: $CELERY_BROKER_URL"
echo "CELERY_RESULT_BACKEND: $CELERY_RESULT_BACKEND"

dagster-celery worker start -A dagster_celery.app -y celery_config.yaml "$@"
