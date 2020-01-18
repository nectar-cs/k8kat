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
  pod.wait_until(pod.has_run)
  logs = pod.raw_logs()
  response = pod_utils.parse_response(logs)
  pod.delete(False)
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
      restart_policy='Never',
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


def one_shot_cmd_body(command):
  return V1Pod(
    api_version='v1',
    metadata=V1ObjectMeta(
      name=f"nectar-curler-{utils.rand_str(5)}",
      labels=dict(owner='nectar', role='curler')
    ),
    spec=V1PodSpec(
      restart_policy='Never',
      containers=[
        V1Container(
          name="primary",
          image='byrnedo/alpine-curl',
          image_pull_policy="IfNotPresent",
          command=command.split(" ")
        )
      ]
    )
  )


def one_shot_cmd(ns, command):
  raw_pod = broker.coreV1.create_namespaced_pod(
    body=one_shot_cmd_body(command),
    namespace=ns
  )
  pod = KatPod(raw_pod)
  pod.wait_until(pod.has_run)
  bundle = dict(code=pod.exit_code, output=pod.raw_logs())
  pod.delete(False)
  return bundle
