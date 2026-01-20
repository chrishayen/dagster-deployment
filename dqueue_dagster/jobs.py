"""
Dagster job definitions using celery_executor.
"""

import random
import subprocess
import time

import dagster as dg
from dagster_celery import celery_executor

from dqueue_dagster.job_configs import get_all_job_ids


class WorkConfig(dg.Config):
    """Configuration for the work op."""

    job_id: str


@dg.op
def process_work(context: dg.OpExecutionContext, config: WorkConfig) -> dict:
    """
    Simulates work that takes 1-3 minutes, then calls an external API (mocked via CLI).
    """
    work_duration = random.uniform(60, 180)
    context.log.info(f"Working on {config.job_id} for {work_duration:.1f}s")
    time.sleep(work_duration)
    result = subprocess.run(
        ["echo", f"Job {config.job_id} completed after {work_duration:.1f}s"],
        capture_output=True,
        text=True,
    )
    return {
        "job_id": config.job_id,
        "duration": work_duration,
        "output": result.stdout.strip(),
    }


def create_job(job_id: str) -> dg.JobDefinition:
    """
    Create a Dagster job for a specific job_id.
    """

    @dg.graph(name=f"{job_id}_graph")
    def job_graph():
        process_work()

    return job_graph.to_job(
        name=job_id,
        executor_def=celery_executor,
        config={
            "execution": {"config": {"broker": {"env": "CELERY_BROKER_URL"}, "backend": {"env": "CELERY_RESULT_BACKEND"}}},
            "ops": {"process_work": {"config": {"job_id": job_id}}},
        },
    )


ALL_JOBS: list[dg.JobDefinition] = [create_job(job_id) for job_id in get_all_job_ids()]
