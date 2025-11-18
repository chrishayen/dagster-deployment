#!/usr/bin/env bash
set -e

CLUSTER_NAME="dagster-local"

echo "Stopping Dagster deployment..."

if ! kubectl cluster-info &> /dev/null; then
    echo "No Kubernetes cluster is running."
    exit 0
fi

echo "Deleting Kubernetes resources..."
kubectl delete -f k8s/web.yaml --ignore-not-found=true
kubectl delete -f k8s/daemon.yaml --ignore-not-found=true
kubectl delete -f k8s/code.yaml --ignore-not-found=true
kubectl delete -f k8s/dask.yaml --ignore-not-found=true
kubectl delete -f k8s/postgres.yaml --ignore-not-found=true
kubectl delete -f k8s/role.yaml --ignore-not-found=true
kubectl delete -f k8s/configmap.yaml --ignore-not-found=true
kubectl delete -f k8s/secret.yaml --ignore-not-found=true

echo ""
echo "Dagster deployment stopped."
echo ""
echo "To delete the entire cluster, run:"
echo "  kind delete cluster --name ${CLUSTER_NAME}"
