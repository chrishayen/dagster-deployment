import os
from dagster import Definitions, asset, DailyPartitionsDefinition, AssetExecutionContext
from dagster_celery import celery_executor


@asset
def my_asset():
    return "Hello, Dagster!"


@asset(partitions_def=DailyPartitionsDefinition(start_date="2025-01-01"))
def my_asset_with_partition(context: AssetExecutionContext):
    return f"Hello, Dagster! {context.partition_key}"


definitions = Definitions(
    assets=[my_asset, my_asset_with_partition],
    executor=celery_executor.configured({
        "broker": os.getenv("CELERY_BROKER_URL", "pyamqp://dagster:dagster@rabbitmq:5672//"),
        "backend": os.getenv("CELERY_BACKEND_URL", "rpc://"),
    }),
)
