#!/bin/bash

docker build . -f CreateKindDockerfile -t kk-test-suite-cluster:latest
docker build . -t k8-kat:latest
docker run -v \
          /var/run/docker.sock:/var/run/docker.sock \
          --net=host \
          kk-test-suite-cluster:latest

