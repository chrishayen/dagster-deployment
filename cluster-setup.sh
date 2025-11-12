#!/usr/bin/env bash
set -e

echo "Setting up local Kubernetes cluster with kind..."

if ! command -v kind &> /dev/null; then
    echo "Error: kind is not installed."
    echo "Please install kind: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed."
    echo "Please install kubectl: https://kubernetes.io/docs/tasks/tools/"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    echo "Error: docker is not installed."
    echo "Please install docker: https://docs.docker.com/get-docker/"
    exit 1
fi

CLUSTER_NAME="dagster-local"

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster '${CLUSTER_NAME}' already exists."
    read -p "Do you want to delete and recreate it? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Deleting existing cluster..."
        kind delete cluster --name ${CLUSTER_NAME}
    else
        echo "Using existing cluster."
        kubectl cluster-info --context kind-${CLUSTER_NAME}
        exit 0
    fi
fi

echo "Creating kind cluster..."
cat <<EOF | kind create cluster --name ${CLUSTER_NAME} --config=-
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 30000
    hostPort: 3000
    protocol: TCP
EOF

echo "Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=60s

echo ""
echo "Cluster setup complete!"
echo "Cluster name: ${CLUSTER_NAME}"
echo "Context: kind-${CLUSTER_NAME}"
echo ""
echo "Next steps:"
echo "  1. Run ./start.sh to build and deploy Dagster"
echo "  2. Access the UI at http://localhost:3000"
