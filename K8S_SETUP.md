# Kubernetes Environment Setup

This guide explains how to set up a local Kubernetes environment for deploying and testing this Dagster project.

## Prerequisites

Before you begin, make sure you have the following tools installed:

### 1. Docker
```bash
# Check if Docker is installed
docker --version

# If not installed, visit: https://docs.docker.com/get-docker/
```

### 2. kubectl
```bash
# Check if kubectl is installed
kubectl version --client

# If not installed:
# macOS: brew install kubectl
# Linux: https://kubernetes.io/docs/tasks/tools/install-kubectl-linux/
# Windows: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/
```

### 3. kind (Kubernetes in Docker)
```bash
# Check if kind is installed
kind version

# If not installed:
# macOS: brew install kind
# Linux/macOS:
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Full instructions: https://kind.sigs.k8s.io/docs/user/quick-start/#installation
```

## Quick Start

Once you have all prerequisites installed, you can get Dagster running in Kubernetes with just a few commands:

### 1. Create the Kubernetes Cluster
```bash
./cluster-setup.sh
```

This will:
- Create a local kind cluster named `dagster-local`
- Configure port mapping for accessing the Dagster UI
- Set up the cluster context

### 2. Build and Deploy
```bash
./start.sh
```

This will:
- Build all Docker images (code server, daemon, webserver)
- Load images into the kind cluster
- Deploy all Kubernetes resources
- Wait for all components to be ready

### 3. Access the Dagster UI
Once deployment is complete, open your browser and navigate to:
```
http://localhost:3000
```

## Helper Scripts

### View Logs
```bash
# View logs for a specific component
./logs.sh <component>

# Available components: web, code, daemon, postgres
./logs.sh web
./logs.sh daemon

# Follow logs in real-time
./logs.sh web --follow
```

### Stop the Deployment
```bash
# Remove all Dagster resources (keeps the cluster running)
./stop.sh

# Delete the entire cluster
kind delete cluster --name dagster-local
```

### Rebuild and Redeploy
```bash
# After making code changes, rebuild and redeploy
./start.sh
```

## Architecture

The deployment consists of the following components:

- **PostgreSQL**: Database for storing run history, event logs, and schedules
- **Code Server**: Hosts the Dagster definitions and pipelines
- **Daemon**: Handles background operations (schedules, sensors, run queuing)
- **Webserver**: Provides the UI for monitoring and managing pipelines

All components run as Kubernetes Deployments with:
- Resource limits for CPU and memory
- Health checks (liveness and readiness probes)
- Automatic restart on failure

## Kubernetes Resources

The deployment creates the following resources:

- **Deployments**: postgres, code, daemon, web
- **Services**: postgres (ClusterIP), code (ClusterIP), web (NodePort)
- **ConfigMap**: dagster-instance (contains dagster.yaml configuration)
- **Secret**: dagster-postgresql-secret (database credentials)
- **RBAC**: Role and RoleBinding for the K8sRunLauncher

## Troubleshooting

### Cluster won't start
```bash
# Check Docker is running
docker ps

# Delete and recreate the cluster
kind delete cluster --name dagster-local
./cluster-setup.sh
```

### Pods not starting
```bash
# Check pod status
kubectl get pods

# View pod details
kubectl describe pod <pod-name>

# Check logs
./logs.sh <component>
```

### Images not found
```bash
# Rebuild and load images
./build.sh
kind load docker-image dagster-code-server --name dagster-local
kind load docker-image dagster-daemon --name dagster-local
kind load docker-image dagster-webserver --name dagster-local
```

### Can't access the UI
```bash
# Check the web service
kubectl get service web

# Check if the web deployment is ready
kubectl get deployment web

# View web logs
./logs.sh web
```

### Database connection issues
```bash
# Check if postgres is running
kubectl get deployment postgres

# View postgres logs
./logs.sh postgres

# Check if the secret exists
kubectl get secret dagster-postgresql-secret
```

## Useful Commands

```bash
# Check cluster info
kubectl cluster-info

# List all resources
kubectl get all

# Check pod status
kubectl get pods

# Check deployment status
kubectl get deployments

# View detailed pod information
kubectl describe pod <pod-name>

# Get a shell in a pod
kubectl exec -it deployment/web -- /bin/bash

# Check cluster nodes
kubectl get nodes
```

## Development Workflow

1. Make changes to your Dagster code in `code/code/main.py`
2. Rebuild and redeploy: `./start.sh`
3. View logs: `./logs.sh code`
4. Test in the UI: http://localhost:3000

## Notes

- This setup uses ephemeral PostgreSQL storage (data is lost on pod restart)
- Images are built locally and loaded into kind (not pushed to a registry)
- The setup is optimized for quick local testing, not production use
- All components run with single replicas
- The web UI is exposed via NodePort on port 30000 (mapped to localhost:3000)
