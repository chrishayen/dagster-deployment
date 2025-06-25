# /opt/dagster/app/my_code_location.py
from dagster import Definitions, asset, DailyPartitionsDefinition, AssetExecutionContext


@asset
def my_asset():
    return "Hello, Dagster!"


@asset(partitions_def=DailyPartitionsDefinition(start_date="2025-01-01"))
def my_asset_with_partition(context: AssetExecutionContext):
    return f"Hello, Dagster! {context.partition_key}"


definitions = Definitions(assets=[my_asset, my_asset_with_partition])
