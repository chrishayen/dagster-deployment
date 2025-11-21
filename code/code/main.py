import os
from dagster import Definitions, asset, DailyPartitionsDefinition, AssetExecutionContext
from dagster_celery import celery_executor


def build_broker_url():
    """Build Celery broker URL from APP_CONFIG_BROKER_CONNECTION_* environment variables."""
    connection_url = os.getenv('APP_CONFIG_BROKER_CONNECTION_URL', 'https://rabbitmq:5672/')
    login = os.getenv('APP_CONFIG_BROKER_CONNECTION_LOGIN', 'dagster')
    password = os.getenv('APP_CONFIG_BROKER_CONNECTION_PASSWORD', 'dagster')

    # Parse connection URL (format: https://host:port/)
    connection_url = connection_url.rstrip('/')

    # Extract host and port
    if '://' in connection_url:
        _, host_info = connection_url.split('://', 1)
    else:
        host_info = connection_url

    if ':' in host_info:
        host, port = host_info.rsplit(':', 1)
    else:
        host = host_info
        port = '5672'

    # Construct pyamqp URL for Celery
    return f"pyamqp://{login}:{password}@{host}:{port}//"


@asset
def my_asset():
    return "Hello, Dagster!"


@asset(partitions_def=DailyPartitionsDefinition(start_date="2025-01-01"))
def my_asset_with_partition(context: AssetExecutionContext):
    return f"Hello, Dagster! {context.partition_key}"


definitions = Definitions(
    assets=[my_asset, my_asset_with_partition],
    executor=celery_executor.configured({
        "broker": build_broker_url(),
        "backend": os.getenv("CELERY_BACKEND_URL", "rpc://"),
    }),
)
