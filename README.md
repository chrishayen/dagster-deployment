# Dagster Deployment with Celery and RabbitMQ

This is a Dagster deployment that uses Celery with RabbitMQ as the message broker to execute assets and partitions.

## Architecture

- **Code Server**: Hosts the Dagster definitions and assets (gRPC server on port 4000)
- **Web Server**: Dagster UI (port 3000)
- **Daemon**: Runs schedules, sensors, and other background tasks
- **Celery Worker**: Executes asset materializations and ops via Celery
- **PostgreSQL**: Stores run history, event logs, and schedules (port 5432)
- **RabbitMQ**: Message broker for Celery (port 5672, management UI on port 15672)

## Prerequisites

- Docker and Docker Compose

## Getting Started

### Build and Start

```bash
# Build images
./build.sh

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Access the UI

- Dagster UI: http://localhost:3000
- RabbitMQ Management: http://localhost:15672 (username: dagster, password: dagster)

### Stop

```bash
docker-compose down

# Or use the stop script
./stop.sh
```

## Project Structure

```
.
├── code/              # Code server (Dagster definitions)
├── daemon/            # Daemon process
├── web/               # Web UI server
├── worker/            # Celery worker
├── compose.yaml       # Docker Compose configuration
├── dagster.yaml       # Dagster instance configuration
├── workspace.yaml     # Workspace configuration
├── Dockerfile         # Multi-app Dockerfile
├── build.sh           # Build script
└── start.sh           # Start script
```

## Configuration

### Celery Configuration

The Celery executor is configured in `dagster.yaml` with:
- Broker: RabbitMQ (pyamqp://dagster:dagster@rabbitmq:5672//)
- Backend: RPC

### Environment Variables

All services use the following environment variables:
- `POSTGRESQL_HOSTNAME=postgres`
- `POSTGRESQL_USERNAME=dagster`
- `POSTGRESQL_PASSWORD=dagster`
- `POSTGRESQL_DB=dagster`
- `CELERY_BROKER_URL=pyamqp://dagster:dagster@rabbitmq:5672//`
- `CELERY_BACKEND_URL=rpc://`

## Adding Assets

Assets are defined in `code/code/main.py`. The Celery executor is configured to run all ops and assets via Celery workers.

Example:

```python
from dagster import asset, AssetExecutionContext

@asset
def my_asset():
    return "Hello, Dagster!"
```

## Development

Each component (code, daemon, web, worker) has its own:
- `pyproject.toml` - Poetry dependencies
- `start.sh` - Entry point script

To make changes:
1. Modify the relevant code
2. Rebuild: `./build.sh`
3. Restart: `docker-compose up -d`
