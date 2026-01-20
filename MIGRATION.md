# Migration: Standard Dagster to Celery Executor

Steps to migrate from standard Dagster (everything runs on code server) to distributed Celery+RabbitMQ execution.

## Prerequisites
- Dagster deployment with PostgreSQL shared state
- Web, daemon, and code server running

## Configuration Steps

### 1. Infrastructure Setup
- [ ] Deploy RabbitMQ (broker for Celery task queue)
- [ ] Ensure PostgreSQL is configured for run storage

### 2. Install Dependencies
- [ ] Add `dagster-celery>=0.27.0` to requirements
- [ ] Add `celery>=5.6.0` to requirements

### 3. Update dagster.yaml
- [ ] Add `QueuedRunCoordinator` with `max_concurrent_runs` setting
- [ ] Verify PostgreSQL storage configuration uses environment variables for hostname

### 4. Create celery_config.yaml
- [ ] Configure broker URL pointing to RabbitMQ
- [ ] Set `include` to your Dagster module(s)

### 5. Modify Job Definitions
- [ ] Import `celery_executor` from `dagster_celery`
- [ ] Update each job to use `executor_def=celery_executor`
- [ ] Add execution config with broker URL to job configs

### 6. Build Separate Worker Image
- [ ] Create Dockerfile for workers (different from webserver/daemon)
- [ ] Workers run: `dagster-celery worker start -A dagster_celery.app -y /path/to/celery_config.yaml`

### 7. Update Deployments
- [ ] Webserver: no executor changes needed (just serves UI)
- [ ] Daemon: no executor changes needed (runs sensors/schedules)
- [ ] Add new worker deployment (runs Celery workers, scalable)

### 8. Environment Variables
- [ ] Set `CELERY_BROKER_URL` for all services
- [ ] Set `DAGSTER_PG_HOST` for all services
- [ ] Ensure `DAGSTER_HOME` points to dagster.yaml location

### 9. Networking
- [ ] Workers need access to RabbitMQ (5672)
- [ ] Workers need access to PostgreSQL (5432)
- [ ] Workers need same code/modules as code server

### 10. Testing
- [ ] Start with 1 worker replica
- [ ] Trigger a job and verify it runs on worker (not code server)
- [ ] Scale workers and verify load distribution

## Architecture Change

The key change: jobs no longer execute on the code server. The daemon submits runs to the queue, workers pick them up from RabbitMQ and execute them.

```
Before:
  Daemon -> Code Server (executes jobs)

After:
  Daemon -> RabbitMQ Queue -> Celery Workers (execute jobs)
```
