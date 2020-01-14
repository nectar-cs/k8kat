import os
import time
from typing import List, Tuple

import yaml
from kubernetes.client import V1Namespace, V1ObjectMeta

from k8_kat.base.broker_configs import default_config
from k8_kat.base.kube_broker import broker
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


def terraform():
  if utils.run_env() == 'production':
    raise Exception('Cannot terraform in production!')

  finder = lambda name: [rd for rd in res_defs if rd['kind'] == name][0]
  sa_name, sa_ns = [default_config()['sa_name'], default_config()['sa_ns']]
  crb_name, context = [default_config()['crb_name'], default_config()['context']]
  kubectl = default_config()['kubectl']

  message = dict(sa_name=sa_name, sa_ns=sa_ns, crb_name=crb_name)
  print(f"Terraforming context {default_config()['context']}: {message}...")

  root = utils.root_path()
  stream = open(os.path.join(root, f"utils/testing/fixtures/ci-perms.yaml"), 'r')

  res_defs = [data for data in yaml.load_all(stream, Loader=yaml.BaseLoader)]
  sa, crb = [finder('ServiceAccount'), finder('ClusterRoleBinding')]
  subject = f"system:serviceaccount:{sa_ns}:{sa_name}"

  sa['metadata']['name'] = sa_name or sa['metadata']['name']
  sa['metadata']['namespace'] = sa_ns or sa['metadata']['namespace']
  crb['metadata']['name'] = crb_name or crb['metadata']['name']
  crb['subjects'][0]['name'] = subject or crb['subjects'][0]['name']

  output = yaml.dump_all([sa, crb])

  cmd = f"echo \"{output}\" | {utils.kmd('apply', k=kubectl, ctx=context)} -f -"
  # print(cmd)
  print(utils.shell_exec(cmd))

  # k_apply(f"ci-perms")
