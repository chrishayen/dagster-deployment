"""
Dagster sensors that auto-start jobs and re-trigger them 2 minutes after completion.
"""

from datetime import datetime, timedelta, timezone

import dagster as dg

from dqueue_dagster.job_configs import get_all_job_ids
from dqueue_dagster.jobs import ALL_JOBS

RERUN_DELAY_SECONDS = 120  # 2 minutes


def create_sensor(job_def: dg.JobDefinition) -> dg.SensorDefinition:
    """
    Create a sensor that:
    1. Auto-triggers the job if it has never run
    2. Re-triggers 2 minutes after last successful completion
    """
    job_name = job_def.name

    @dg.sensor(
        name=f"{job_name}_sensor",
        job=job_def,
        minimum_interval_seconds=30,
        default_status=dg.DefaultSensorStatus.RUNNING,
    )
    def job_sensor(context: dg.SensorEvaluationContext):
        runs = context.instance.get_runs(
            filters=dg.RunsFilter(job_name=job_name),
            limit=1,
        )

        # No runs yet - trigger immediately
        if not runs:
            context.log.info(f"No runs found for {job_name}, triggering initial run")
            return dg.RunRequest(run_key=f"{job_name}_initial")

        last_run = runs[0]

        # If there's a run in progress, skip
        if last_run.status in [
            dg.DagsterRunStatus.STARTED,
            dg.DagsterRunStatus.STARTING,
            dg.DagsterRunStatus.QUEUED,
            dg.DagsterRunStatus.NOT_STARTED,
        ]:
            return dg.SkipReason(f"Job {job_name} is currently running")

        # If last run failed, retry immediately
        if last_run.status == dg.DagsterRunStatus.FAILURE:
            context.log.info(f"Last run of {job_name} failed, retrying")
            return dg.RunRequest(
                run_key=f"{job_name}_retry_{datetime.now(timezone.utc).isoformat()}"
            )

        # If last run succeeded, check if 2 minutes have passed
        if last_run.status == dg.DagsterRunStatus.SUCCESS:
            run_stats = context.instance.get_run_stats(last_run.run_id)
            end_time = run_stats.end_time
            if end_time is None:
                return dg.SkipReason("Run completed but no end time recorded")

            elapsed = datetime.now(timezone.utc).timestamp() - end_time
            if elapsed >= RERUN_DELAY_SECONDS:
                context.log.info(
                    f"Job {job_name} completed {elapsed:.0f}s ago, re-triggering"
                )
                return dg.RunRequest(
                    run_key=f"{job_name}_{datetime.now(timezone.utc).isoformat()}"
                )
            else:
                remaining = RERUN_DELAY_SECONDS - elapsed
                return dg.SkipReason(
                    f"Waiting {remaining:.0f}s before re-triggering {job_name}"
                )

        return dg.SkipReason(f"Unexpected run status: {last_run.status}")

    return job_sensor


# Create a mapping from job name to job definition for easy lookup
JOB_MAP = {job.name: job for job in ALL_JOBS}

# Create all sensors
ALL_SENSORS: list[dg.SensorDefinition] = [
    create_sensor(job_def) for job_def in ALL_JOBS
]
