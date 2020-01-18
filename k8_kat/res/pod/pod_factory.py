from kubernetes.client import V1PodSpec, V1Container, V1ObjectMeta, V1Pod

from k8_kat.auth.kube_broker import broker
from k8_kat.res.pod import pod_utils
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.utils.main import utils


def one_shot_curl(ns, **kwargs):
  raw_pod = broker.coreV1.create_namespaced_pod(
    body=one_shot_curler_body(**kwargs),
    namespace=ns
  )
  pod = KatPod(raw_pod)
  print(f"Waiting for one-shot-curler...")
  pod.wait_until(pod.has_run)
  print(f"It's now {pod.status}")
  logs = pod.raw_logs()
  response = pod_utils.parse_response(logs)
  print(f"Returned: {logs}")
  # pod.delete(False)
  return response


def one_shot_curler_body(**kwargs):
  args = pod_utils.build_curl_cmd(**kwargs, with_command=False)

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
          args=args
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
