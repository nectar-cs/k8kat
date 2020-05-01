import os
from typing import List, Tuple

from k8_kat.auth.broker_configs import default_config
from k8_kat.auth.kube_broker import broker
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.utils.main import utils
from k8_kat.utils.testing import simple_pod, simple_svc, simple_dep

NAMESPACES = ['n1', 'n2', 'n3']


def create_dep(ns: str, name: str, **subs):
  return simple_dep.create(ns=ns, name=name, **subs)


def create_svc(ns: str, name: str, **subs):
  return simple_svc.create(name=name, ns=ns, **subs)


def create_pod(ns: str, name: str, **subs) -> KatPod:
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
