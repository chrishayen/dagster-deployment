#!/usr/bin/env bash

kubectl delete -f k8s/web.yaml
kubectl delete -f k8s/daemon.yaml
kubectl delete -f k8s/code.yaml
kubectl delete -f k8s/role.yaml

kubectl apply -f k8s/role.yaml
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/daemon.yaml
kubectl apply -f k8s/code.yaml
kubectl apply -f k8s/web.yaml


echo "To access run kubectl port-forward pod/web 3000:3000 the go to http://localhost:3000"