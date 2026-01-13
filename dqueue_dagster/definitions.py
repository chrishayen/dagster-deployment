"""
Dagster definitions entry point.
"""

import dagster as dg

from dqueue_dagster.jobs import ALL_JOBS
from dqueue_dagster.sensors import ALL_SENSORS

defs = dg.Definitions(
    jobs=ALL_JOBS,
    sensors=ALL_SENSORS,
)
