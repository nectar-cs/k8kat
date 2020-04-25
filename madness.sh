#!/bin/bash


kind delete cluster
kind create cluster
kubectl config use-context kind-kind

./test-eval.sh