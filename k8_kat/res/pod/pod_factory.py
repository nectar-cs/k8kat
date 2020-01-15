import time

from kubernetes.client import V1PodSpec, V1Container, V1ObjectMeta, V1Pod

from k8_kat.auth.kube_broker import broker


def curl_pod(ns, name):
  pod = V1Pod(
    api_version='v1',
    metadata=V1ObjectMeta(
      name=name,
      labels={"nectar-type": "stunt-pod"}
    ),
    spec=V1PodSpec(
      containers=[
        V1Container(
          name="primary",
          image='xnectar/curler:latest',
          image_pull_policy="Always"
        )
      ]
    )
  )

  return broker.coreV1.create_namespaced_pod(
    body=pod,
    namespace=ns
  )
