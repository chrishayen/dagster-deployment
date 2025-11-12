#!/usr/bin/env bash
set -e

echo "Starting Dagster deployment..."
echo ""

echo "Step 1: Building Docker images..."
./build.sh

echo ""
echo "Step 2: Deploying to Kubernetes..."
./deploy.sh

echo ""
echo "All done! Dagster is now running."
echo "Access the UI at: http://localhost:3000"
