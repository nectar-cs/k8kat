import os
from typing import List, Tuple

from kubernetes.client import V1Namespace, V1ObjectMeta

from k8_kat.base.broker_configs import default_config
from k8_kat.base.kube_broker import broker
from utils.testing.fixtures import simple_dep, simple_svc, simple_pod
from utils.main.utils import Utils

NAMESPACES = ['n1', 'n2', 'n3']

class TestEnv:

  @staticmethod
  def create_dep(ns: str, name: str, **subs):
    simple_dep.create(ns=ns, name=name, **subs)

  @staticmethod
  def create_svc(ns: str, name: str, **subs):
    simple_svc.create(name=name, ns=ns, **subs)

  @staticmethod
  def create_pod(ns: str, name: str, **subs):
    simple_pod.create(name=name, ns=ns, **subs)

  @staticmethod
  def nk_label_dep(ns: str, name: str, labels: List[Tuple[str, str]]):
    api = broker.appsV1Api
    dep = api.read_namespaced_deployment(namespace=ns, name=name)
    dep.metadata.labels = {t[0]: t[1] for t in labels}
    api.patch_namespaced_deployment(namespace=ns,name=name,body=dep)

  @staticmethod
  def k(cmd: str):
    kubectl = default_config()['kubectl']
    final_command = f"{kubectl} {cmd}"
    os.system(final_command)

  @staticmethod
  def nk(cmd: str, ns: str, ctx: str=None):
    cmd = f"{cmd} -n {ns}" if ns else cmd
    cmd = f"{cmd} --context={ctx}" if ctx else cmd
    TestEnv.k(cmd)

  @staticmethod
  def k_apply(filename, ns, ctx):
    root = Utils.root_path()
    filename = os.path.join(root, f"utils/testing/fixtures/{filename}.yaml")
    TestEnv.nk(f"apply -f {filename}", ns, ctx)

  @staticmethod
  def create_namespaces():
    api = broker.coreV1
    crt_nss = [ns.metadata.name for ns in api.list_namespace().items]

    for desired_ns in NAMESPACES:
      if not desired_ns in crt_nss:
        api.create_namespace(
          body=V1Namespace(
            metadata=V1ObjectMeta(
              name=desired_ns
            )
          )
        )

  @staticmethod
  def cleanup():
    crt_nss = [ns.metadata.name for ns in broker.coreV1.list_namespace()]

    if Utils.is_ci() and not Utils.is_ci_keep():
      for ns in list(set(crt_nss) & set(NAMESPACES)):
        broker.coreV1.delete_namespace(ns)
      else:
        for ns in NAMESPACES:
          broker.appsV1Api.delete_collection_namespaced_deployment(namespace=ns)
          broker.coreV1.delete_collection_namespaced_service(namespace=ns)

  @staticmethod
  def delete_pods(namespaces):
    namespaces = namespaces if namespaces else NAMESPACES
    for ns in namespaces:
      broker.coreV1.delete_collection_namespaced_pod(namespace=ns)

  @staticmethod
  def terraform():
    context = default_config()['context']
    TestEnv.k_apply(f"ci-perms", None, context)
