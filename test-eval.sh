#!/bin/bash

kind load docker-image test-run:latest
kubectl delete pod -l app=runner -n default
kubectl apply -f runner.yaml

status=$(kubectl get pod/runner -o json | jq .status.phase -r)

while [[ "$status" == "Pending" ]] || [[ "$status" == "ContainerCreating" ]] || [[ "$status" == "Running" ]]; do
  status=$(kubectl get pod/runner -o json | jq .status.phase -r)
  kubectl get pod
  sleep 2
done

kubectl logs runner

if [[ "$status" == "Succeeded" ]]; then
  echo "Exit code 0"
  exit 0
else
    echo "Exit code 1: $status"
  exit 1
fi
