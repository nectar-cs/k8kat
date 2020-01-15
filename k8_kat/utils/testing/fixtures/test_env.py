import os
import time
from typing import List, Tuple

from kubernetes.client import V1Namespace, V1ObjectMeta

from k8_kat.auth.broker_configs import default_config
from k8_kat.auth.kube_broker import broker
from k8_kat.utils.testing.fixtures import simple_pod, simple_dep, simple_svc
from k8_kat.utils.main import utils

NAMESPACES = ['n1', 'n2', 'n3']


def create_dep(ns: str, name: str, **subs):
  return simple_dep.create(ns=ns, name=name, **subs)


def create_svc(ns: str, name: str, **subs):
  return simple_svc.create(name=name, ns=ns, **subs)


def create_pod(ns: str, name: str, **subs):
  return simple_pod.create(name=name, ns=ns, **subs)


def nk_label_dep(ns: str, name: str, labels: List[Tuple[str, str]]):
  api = broker.appsV1Api
  dep = api.read_namespaced_deployment(namespace=ns, name=name)
  dep.metadata.labels = {t[0]: t[1] for t in labels}
  api.patch_namespaced_deployment(namespace=ns, name=name, body=dep)


def k_apply(filename, **kwargs):
  config = default_config()
  root = utils.root_path()
  filename = os.path.join(root, f"utils/testing/fixtures/{filename}.yaml")
  kubectl, context = config['kubectl'], config['context']
  utils.k_exec(f"apply -f {filename}", k=kubectl, ctx=context, **kwargs)


def create_namespaces():
  api = broker.coreV1
  crt_nss = [ns.metadata.name for ns in api.list_namespace().items]

  for desired_ns in NAMESPACES:
    if desired_ns not in crt_nss:
      api.create_namespace(
        body=V1Namespace(metadata=V1ObjectMeta(name=desired_ns))
      )


def cleanup():
  api = broker.coreV1
  crt_nss = lambda: [_ns.metadata.name for _ns in api.list_namespace().items]
  victim_namespaces = lambda: list(set(crt_nss()) & set(NAMESPACES))
  for ns in victim_namespaces():
    broker.coreV1.delete_namespace(ns)

  try:
    if len(victim_namespaces()):
      print(f"[test_env] Waiting for ns {victim_namespaces()} to be destroyed...")

    while len(victim_namespaces()):
      time.sleep(2)
  except Exception as e:
    print(f"[test_env] Error {str(e)} monitoring ns destruction")
    pass


