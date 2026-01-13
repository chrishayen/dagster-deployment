"""
Configuration for the 200 jobs.
Each job has a configurable number of tasks to spawn.
"""

import random

NUM_JOBS = 200

# Generate configurations for all jobs
# Each job spawns between 3-15 tasks (configurable per job)
JOB_CONFIGS: dict[str, dict] = {}

random.seed(42)  # Deterministic for reproducibility

for i in range(NUM_JOBS):
    job_id = f"job_{i:03d}"
    JOB_CONFIGS[job_id] = {
        "num_tasks": random.randint(3, 15),
    }


def get_job_config(job_id: str) -> dict:
    """Get the configuration for a specific job."""
    return JOB_CONFIGS.get(job_id, {"num_tasks": 5})


def get_all_job_ids() -> list[str]:
    """Get all job IDs."""
    return list(JOB_CONFIGS.keys())
