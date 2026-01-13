# Distributed Job Queue with Dagster and Celery

A scalable job orchestration system using Dagster for scheduling/monitoring and Celery workers for distributed task execution over RabbitMQ.

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Dagster        │     │  Dagster        │     │   PostgreSQL    │
│  Webserver      │────▶│  Daemon         │────▶│   (run storage) │
│  (UI :3000)     │     │  (sensors)      │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                                 ▼
                        ┌─────────────────┐
                        │    RabbitMQ     │
                        │   (broker)      │
                        └────────┬────────┘
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
┌───────────────┐       ┌───────────────┐       ┌───────────────┐
│ Celery Worker │       │ Celery Worker │  ...  │ Celery Worker │
│      (1)      │       │      (2)      │       │     (N)       │
└───────────────┘       └───────────────┘       └───────────────┘
```

### Components

- **Dagster Webserver**: UI for monitoring jobs, runs, and sensors
- **Dagster Daemon**: Runs sensors that trigger jobs on schedule
- **PostgreSQL**: Shared storage for run state (scalable, unlike SQLite)
- **RabbitMQ**: Message broker for Celery task distribution
- **Celery Workers**: Execute job steps via `dagster-celery` executor

### How It Works

1. Sensors check if jobs need to run (initial trigger or 2 min after completion)
2. Dagster daemon launches runs and submits steps to Celery queue
3. Workers pick up steps from RabbitMQ and execute them
4. Results are stored in PostgreSQL, visible in Dagster UI

## Local Development (Docker Compose)

### Prerequisites

- Docker and Docker Compose

### Quick Start

```bash
# Start all services (20 workers by default)
docker-compose up -d

# View logs
docker-compose logs -f

# Scale workers
docker-compose up -d --scale worker=50

# Stop and clean up
docker-compose down -v
```

### Access Points

- Dagster UI: http://localhost:3000
- RabbitMQ Management: http://localhost:15672 (guest/guest)

## Configuration

### Job Configuration

Edit `dqueue_dagster/job_configs.py` to change:
- Number of jobs (`NUM_JOBS`)
- Per-job settings (tasks per job, etc.)

### Sensor Timing

Edit `dqueue_dagster/sensors.py`:
- `RERUN_DELAY_SECONDS`: Time between job completions and re-trigger (default: 120s)
- `minimum_interval_seconds`: How often sensors check (default: 30s)

### Concurrency

Edit `dagster.yaml`:
```yaml
run_coordinator:
  config:
    max_concurrent_runs: 200  # Adjust based on capacity
```

### Worker Scaling

In `docker-compose.yml`:
```yaml
worker:
  deploy:
    replicas: 20  # Number of worker containers
```

Each worker runs multiple processes (default: CPU count). Total capacity = replicas x processes.

## Production Deployment (Kubernetes/OpenShift)

### Helm Chart Structure

```
helm/dagster-celery/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── configmap.yaml          # dagster.yaml, celery_config.yaml
│   ├── deployment-webserver.yaml
│   ├── deployment-daemon.yaml
│   ├── deployment-worker.yaml
│   ├── service-webserver.yaml
│   ├── secret-postgres.yaml
│   └── hpa-worker.yaml         # Horizontal Pod Autoscaler
```

### Key values.yaml Settings

```yaml
# Image configuration
image:
  repository: your-registry/dqueue
  tag: latest
  pullPolicy: Always

# PostgreSQL (use external or subchart)
postgresql:
  enabled: true  # or use external
  auth:
    username: dagster
    password: dagster
    database: dagster
  # For external:
  # external:
  #   host: postgres.example.com
  #   port: 5432

# RabbitMQ (use external or subchart)
rabbitmq:
  enabled: true
  auth:
    username: guest
    password: guest
  # For external:
  # external:
  #   host: rabbitmq.example.com
  #   port: 5672

# Dagster Webserver
webserver:
  replicas: 1
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"
    limits:
      memory: "1Gi"
      cpu: "1"
  service:
    type: ClusterIP
    port: 3000

# Dagster Daemon
daemon:
  replicas: 1
  resources:
    requests:
      memory: "512Mi"
      cpu: "250m"

# Celery Workers
worker:
  replicas: 20
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
  autoscaling:
    enabled: true
    minReplicas: 5
    maxReplicas: 100
    targetCPUUtilization: 70

# Dagster configuration
dagster:
  maxConcurrentRuns: 200
```

### ConfigMap for dagster.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: dagster-config
data:
  dagster.yaml: |
    run_coordinator:
      module: dagster.core.run_coordinator
      class: QueuedRunCoordinator
      config:
        max_concurrent_runs: {{ .Values.dagster.maxConcurrentRuns }}

    storage:
      postgres:
        postgres_db:
          username: {{ .Values.postgresql.auth.username }}
          password: {{ .Values.postgresql.auth.password }}
          hostname: {{ include "postgresql.hostname" . }}
          db_name: {{ .Values.postgresql.auth.database }}
          port: 5432

    telemetry:
      enabled: false

  celery_config.yaml: |
    execution:
      config:
        broker: "pyamqp://{{ .Values.rabbitmq.auth.username }}:{{ .Values.rabbitmq.auth.password }}@{{ include "rabbitmq.hostname" . }}:5672//"
        include: ["dqueue_dagster"]
```

### Worker Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dagster-celery-worker
spec:
  replicas: {{ .Values.worker.replicas }}
  selector:
    matchLabels:
      app: dagster-celery-worker
  template:
    metadata:
      labels:
        app: dagster-celery-worker
    spec:
      containers:
      - name: worker
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        command:
          - dagster-celery
          - worker
          - start
          - -A
          - dagster_celery.app
          - -y
          - /app/celery_config.yaml
        env:
        - name: DAGSTER_HOME
          value: /opt/dagster/dagster_home
        - name: DAGSTER_PG_HOST
          value: {{ include "postgresql.hostname" . }}
        - name: CELERY_BROKER_URL
          value: "amqp://{{ .Values.rabbitmq.auth.username }}:{{ .Values.rabbitmq.auth.password }}@{{ include "rabbitmq.hostname" . }}:5672//"
        resources:
          {{- toYaml .Values.worker.resources | nindent 10 }}
        volumeMounts:
        - name: dagster-config
          mountPath: /opt/dagster/dagster_home/dagster.yaml
          subPath: dagster.yaml
        - name: dagster-config
          mountPath: /app/celery_config.yaml
          subPath: celery_config.yaml
      volumes:
      - name: dagster-config
        configMap:
          name: dagster-config
```

### OpenShift-Specific Considerations

1. **Security Context Constraints (SCC)**:
   ```yaml
   securityContext:
     runAsNonRoot: true
     runAsUser: 1000
   ```

2. **Routes instead of Ingress**:
   ```yaml
   apiVersion: route.openshift.io/v1
   kind: Route
   metadata:
     name: dagster-webserver
   spec:
     to:
       kind: Service
       name: dagster-webserver
     port:
       targetPort: 3000
     tls:
       termination: edge
   ```

3. **ImageStreams** for internal registry:
   ```yaml
   apiVersion: image.openshift.io/v1
   kind: ImageStream
   metadata:
     name: dqueue
   ```

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: dagster-celery-worker
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: dagster-celery-worker
  minReplicas: {{ .Values.worker.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.worker.autoscaling.maxReplicas }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ .Values.worker.autoscaling.targetCPUUtilization }}
```

## Customizing Jobs

### Adding Real Work

Replace the simulated work in `dqueue_dagster/jobs.py`:

```python
@dg.op
def process_work(context: dg.OpExecutionContext, config: WorkConfig) -> dict:
    # Your actual work here
    result = call_external_api(config.job_id)
    return {"job_id": config.job_id, "result": result}
```

### Adding Multiple Steps per Job

Use Dagster's dynamic outputs for fan-out:

```python
@dg.op(out=dg.DynamicOut())
def generate_tasks(config: WorkConfig):
    for i in range(config.num_tasks):
        yield dg.DynamicOutput(
            {"task_id": f"{config.job_id}_task_{i}"},
            mapping_key=str(i)
        )

@dg.op
def process_task(task_info: dict) -> dict:
    # Process individual task
    return {"task_id": task_info["task_id"], "status": "done"}

@dg.graph
def job_graph():
    tasks = generate_tasks()
    results = tasks.map(process_task)
    return results.collect()
```

## Monitoring

### Dagster UI

- View run status, logs, and Gantt charts
- Monitor sensor activity
- See queue depth and worker activity

### RabbitMQ Management

- Queue depth indicates backlog
- Consumer count shows active workers
- Message rates show throughput

### Metrics to Watch

- `dagster_run_count`: Runs by status
- RabbitMQ queue length
- Worker CPU/memory utilization
- PostgreSQL connection count

## Troubleshooting

### Workers Not Processing

1. Check worker logs: `docker logs dqueue-worker-1`
2. Verify RabbitMQ connectivity
3. Ensure `DAGSTER_HOME` and `DAGSTER_PG_HOST` are set

### Sensors Not Triggering

1. Check daemon logs: `docker logs dqueue-dagster-daemon-1`
2. Verify sensors are enabled in UI
3. Check PostgreSQL connectivity

### Jobs Stuck in Queue

1. Check `max_concurrent_runs` in dagster.yaml
2. Verify worker count and health
3. Check RabbitMQ queue depth

## License

MIT
