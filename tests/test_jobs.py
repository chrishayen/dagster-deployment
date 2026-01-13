"""
Tests for Dagster jobs with celery_executor.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestJobConfigs:
    def test_job_configs_has_200_jobs(self):
        from dqueue_dagster.job_configs import JOB_CONFIGS, NUM_JOBS

        assert NUM_JOBS == 200
        assert len(JOB_CONFIGS) == 200

    def test_all_jobs_have_num_tasks_config(self):
        from dqueue_dagster.job_configs import JOB_CONFIGS

        for job_id, config in JOB_CONFIGS.items():
            assert "num_tasks" in config
            assert isinstance(config["num_tasks"], int)
            assert 3 <= config["num_tasks"] <= 15

    def test_get_job_config_returns_correct_config(self):
        from dqueue_dagster.job_configs import JOB_CONFIGS, get_job_config

        config = get_job_config("job_000")
        assert config == JOB_CONFIGS["job_000"]

    def test_get_job_config_returns_default_for_unknown_job(self):
        from dqueue_dagster.job_configs import get_job_config

        config = get_job_config("unknown_job")
        assert config == {"num_tasks": 5}

    def test_get_all_job_ids_returns_all_ids(self):
        from dqueue_dagster.job_configs import get_all_job_ids

        job_ids = get_all_job_ids()
        assert len(job_ids) == 200
        assert "job_000" in job_ids
        assert "job_199" in job_ids


class TestDagsterJobs:
    def test_all_jobs_are_created(self):
        from dqueue_dagster.jobs import ALL_JOBS

        assert len(ALL_JOBS) == 200

    def test_jobs_have_correct_names(self):
        from dqueue_dagster.jobs import ALL_JOBS

        job_names = {job.name for job in ALL_JOBS}
        assert "job_000" in job_names
        assert "job_199" in job_names

    def test_jobs_use_celery_executor(self):
        from dagster_celery import celery_executor
        from dqueue_dagster.jobs import ALL_JOBS

        for job in ALL_JOBS:
            assert job.executor_def == celery_executor


class TestDagsterSensors:
    def test_all_sensors_are_created(self):
        from dqueue_dagster.sensors import ALL_SENSORS

        assert len(ALL_SENSORS) == 200

    def test_sensors_have_correct_names(self):
        from dqueue_dagster.sensors import ALL_SENSORS

        sensor_names = {sensor.name for sensor in ALL_SENSORS}
        assert "job_000_sensor" in sensor_names
        assert "job_199_sensor" in sensor_names


class TestDefinitions:
    def test_definitions_has_all_jobs_and_sensors(self):
        from dqueue_dagster.definitions import defs

        assert len(defs.jobs) == 200
        assert len(defs.sensors) == 200


class TestProcessWorkOp:
    @patch("dqueue_dagster.jobs.subprocess.run")
    @patch("dqueue_dagster.jobs.time.sleep")
    @patch("dqueue_dagster.jobs.random.uniform")
    def test_process_work_returns_expected_result(
        self, mock_uniform, mock_sleep, mock_subprocess
    ):
        mock_uniform.return_value = 90.0
        mock_subprocess.return_value = MagicMock(
            stdout="Job test_job completed after 90.0s"
        )

        import dagster as dg
        from dqueue_dagster.jobs import WorkConfig, process_work

        context = dg.build_op_context()
        config = WorkConfig(job_id="test_job")

        result = process_work(context, config)

        assert result["job_id"] == "test_job"
        assert result["duration"] == 90.0
        assert "completed" in result["output"]

    @patch("dqueue_dagster.jobs.subprocess.run")
    @patch("dqueue_dagster.jobs.time.sleep")
    @patch("dqueue_dagster.jobs.random.uniform")
    def test_process_work_sleeps_for_random_duration(
        self, mock_uniform, mock_sleep, mock_subprocess
    ):
        mock_uniform.return_value = 120.5
        mock_subprocess.return_value = MagicMock(stdout="done")

        import dagster as dg
        from dqueue_dagster.jobs import WorkConfig, process_work

        context = dg.build_op_context()
        config = WorkConfig(job_id="test_job")

        process_work(context, config)

        mock_uniform.assert_called_once_with(60, 180)
        mock_sleep.assert_called_once_with(120.5)
