#!/bin/bash


kind delete cluster
kind create cluster
kubectl config use-context kind-kind

kind load docker-image test-run:latest

