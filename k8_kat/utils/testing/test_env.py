import os
import time
from threading import Thread
from typing import List, Tuple

from kubernetes.client import V1Namespace, V1ObjectMeta

from k8_kat.auth.broker_configs import default_config
from k8_kat.auth.kube_broker import broker
from k8_kat.utils.testing import simple_pod, simple_svc, simple_dep
from k8_kat.utils.main import utils

NAMESPACES = ['n1', 'n2', 'n3']


def create_dep(ns: str, name: str, **subs):
  return simple_dep.create(ns=ns, name=name, **subs)


def create_svc(ns: str, name: str, **subs):
  return simple_svc.create(name=name, ns=ns, **subs)


def create_pod(ns: str, name: str, **subs):
  return simple_pod.create(name=name, ns=ns, **subs)


def nk_label_dep(ns: str, name: str, labels: List[Tuple[str, str]]):
  api = broker.appsV1
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

def pod_wiper(ns):
  broker.coreV1.delete_collection_namespaced_pod(ns)

def dep_wiper(ns):
  broker.appsV1.delete_collection_namespaced_deployment(ns)

def svc_wiper(ns):
  api = broker.coreV1
  svcs = api.list_namespaced_service(ns).items
  for svc in svcs:
    api.delete_namespaced_service(
      namespace=ns, name=svc.metadata.name
    )

def is_ns_clean(ns):
  if len(broker.coreV1.list_namespaced_pod(ns).items):
    return False

  if len(broker.coreV1.list_namespaced_service(ns).items):
    return False

  if len(broker.appsV1.list_namespaced_deployment(ns).items):
    return False

  return True

def dirty_namespaces():
  return [ns for ns in NAMESPACES if not is_ns_clean(ns)]

def _cleanup():
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


def cleanup():
  threads = []
  for ns in NAMESPACES:
    threads.append(Thread(target=pod_wiper, args=(ns,)))
    threads.append(Thread(target=dep_wiper, args=(ns,)))
    threads.append(Thread(target=svc_wiper, args=(ns,)))

  [thread.start() for thread in threads]
  [thread.join() for thread in threads]

  try:
    if len(dirty_namespaces()):
      print(f"[test_env] Waiting for ns {dirty_namespaces()} res's to be destroyed...")

    while len(dirty_namespaces()):
      time.sleep(1)
  except Exception as e:
    print(f"[test_env] Error {str(e)} monitoring ns destruction")
    pass
