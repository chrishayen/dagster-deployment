#!/usr/bin/env bash

COMPONENT=$1
FOLLOW=${2:-""}

if [ -z "$COMPONENT" ]; then
    echo "Usage: ./logs.sh <component> [--follow]"
    echo ""
    echo "Available components:"
    echo "  web              - Dagster webserver"
    echo "  code             - Dagster code server"
    echo "  daemon           - Dagster daemon"
    echo "  postgres         - PostgreSQL database"
    echo "  dask-scheduler   - Dask scheduler"
    echo "  dask-worker      - Dask workers"
    echo ""
    echo "Examples:"
    echo "  ./logs.sh web"
    echo "  ./logs.sh daemon --follow"
    echo "  ./logs.sh dask-scheduler --follow"
    exit 1
fi

if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster."
    exit 1
fi

FOLLOW_FLAG=""
if [ "$FOLLOW" == "--follow" ] || [ "$FOLLOW" == "-f" ]; then
    FOLLOW_FLAG="-f"
fi

case $COMPONENT in
    web|code|daemon|postgres|dask-scheduler|dask-worker)
        LABEL="app=$COMPONENT"
        ;;
    *)
        echo "Error: Unknown component '$COMPONENT'"
        echo "Available: web, code, daemon, postgres, dask-scheduler, dask-worker"
        exit 1
        ;;
esac

echo "Fetching logs for $COMPONENT..."
kubectl logs -l $LABEL $FOLLOW_FLAG --tail=100
