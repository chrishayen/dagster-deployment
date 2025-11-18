from dagster import Definitions, asset, DailyPartitionsDefinition, AssetExecutionContext, define_asset_job, fs_io_manager
from dagster_dask import dask_executor


@asset
def my_asset():
    return "Hello, Dagster from Dask!"


@asset(partitions_def=DailyPartitionsDefinition(start_date="2025-01-01"))
def my_asset_with_partition(context: AssetExecutionContext):
    return f"Hello, Dagster from Dask! {context.partition_key}"


dask_job = define_asset_job(
    name="dask_job",
    selection="*",
    executor_def=dask_executor,
    config={
        "execution": {
            "config": {
                "cluster": {
                    "existing": {
                        "address": "dask-scheduler:8786",
                        "timeout": 30
                    }
                }
            }
        }
    }
)

definitions = Definitions(
    assets=[my_asset, my_asset_with_partition],
    jobs=[dask_job],
    resources={
        "io_manager": fs_io_manager.configured({"base_dir": "/tmp/dagster-io"})
    }
)
