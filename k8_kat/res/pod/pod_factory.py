from kubernetes.client import V1PodSpec, V1Container, V1ObjectMeta, V1Pod

from k8_kat.auth.kube_broker import broker
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.utils.main import utils


def one_shot_curl(ns, curl_cmd):
  raw_pod = broker.coreV1.create_namespaced_pod(
    body=one_shot_curler_body(curl_cmd),
    namespace=ns
  )
  pod = KatPod(raw_pod)
  pod.wait_until(pod.has_run)
  logs = pod.logs()
  pod.delete(False)
  return logs


def one_shot_curler_body(curl_cmd):
  return V1Pod(
    api_version='v1',
    metadata=V1ObjectMeta(
      name=f"nectar-curler-{utils.rand_str(5)}",
      labels=dict(owner='nectar', role='curler')
    ),
    spec=V1PodSpec(
      containers=[
        V1Container(
          name="primary",
          image='byrnedo/alpine-curl',
          image_pull_policy="IfNotPresent",
          args=curl_cmd
        )
      ]
    )
  )


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
