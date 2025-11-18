#!/usr/bin/env bash
set -e

CLUSTER_NAME="dagster-local"

echo "Deploying Dagster to Kubernetes..."

if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster."
    echo "Run ./cluster-setup.sh first to create a local cluster."
    exit 1
fi

echo "Loading Docker images into kind cluster..."
kind load docker-image dagster-code-server --name ${CLUSTER_NAME}
kind load docker-image dagster-daemon --name ${CLUSTER_NAME}
kind load docker-image dagster-webserver --name ${CLUSTER_NAME}

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/role.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/dask.yaml
kubectl apply -f k8s/code.yaml
kubectl apply -f k8s/daemon.yaml
kubectl apply -f k8s/web.yaml

echo ""
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=120s deployment/postgres
kubectl wait --for=condition=available --timeout=120s deployment/dask-scheduler
kubectl wait --for=condition=available --timeout=120s deployment/dask-worker
kubectl wait --for=condition=available --timeout=120s deployment/code
kubectl wait --for=condition=available --timeout=120s deployment/daemon
kubectl wait --for=condition=available --timeout=120s deployment/web

echo ""
echo "Deployment complete!"
echo ""
echo "Access the Dagster UI at: http://localhost:3000"
echo ""
echo "Useful commands:"
echo "  ./logs.sh <component>  - View logs (component: web, code, daemon, postgres)"
echo "  ./stop.sh              - Stop and clean up everything"
echo "  kubectl get pods       - Check pod status"