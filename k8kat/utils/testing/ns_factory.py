import re
import time
from threading import Thread
from typing import Tuple, List

from kubernetes.client import V1Namespace, V1ObjectMeta
from kubernetes.client.rest import ApiException

from k8kat.auth.kube_broker import broker
from k8kat.res.ns.kat_ns import KatNs

config = dict(
  max_ns=15
)

def possible_names():
  return [make_name(i) for i in range(max_ns())]


def max_ns() -> int:
  return config['max_ns']

def update_max_ns(new_max_ns):
  assert new_max_ns >= max_ns()
  config['max_ns'] = new_max_ns


def make_name(index: int) -> str:
  return f"ns{index + 1}"


def is_nectar_test_ns(name: str) -> bool:
  return re.search("^ns(\d*)$", name) is not None


def create_ns(name) -> str:
  broker.coreV1.create_namespace(
    body=V1Namespace(metadata=V1ObjectMeta(name=name))
  )

  kat_ns = KatNs.find(name)
  while not (kat_ns and kat_ns.is_work_ready()):
    kat_ns = KatNs.find(name, name)
    time.sleep(.5)
  return name


def get_ns() -> List[Tuple[str, str]]:
  api = broker.coreV1
  simplified = lambda n: (n.metadata.name, n.status.phase)
  all_cluster_ns = [simplified(ns) for ns in api.list_namespace().items]
  return [ns for ns in all_cluster_ns if is_nectar_test_ns(ns[0])]


def avail_now_names(crt_list) -> List[str]:
  crt_names = [ns[0] for ns in crt_list]
  terminating = terminating_names(crt_list)
  return list(set(possible_names()) - set(crt_names) - set(terminating))


def terminating_names(crt_list) -> List[str]:
  return [ns[0] for ns in crt_list if ns[1] == 'Terminating']


def running_names(crt_list) -> List[str]:
  return [ns[0] for ns in crt_list if ns[1] == 'Active']


def wait_for_term(wait_for_n: int):
  print(f"Waiting for {wait_for_n} namespaces to finish being destroyed...")
  while len(avail_now_names(get_ns())) < wait_for_n:
    time.sleep(1)


def destroy_ns(name):
  try:
    broker.coreV1.delete_namespace(name)
  except ApiException:
    pass


def initiate_ns_destroy(name):
  Thread(target=destroy_ns, args=(name,)).start()


def destroy_namespaces_async(terminating, count, spared: List[str]):
  victim_names = set(possible_names()) - set(terminating) - set(spared)

  if victim_names >= count:
    victim_names = victim_names[:count]
    for victim_name in victim_names:
      initiate_ns_destroy(victim_name)
  else:
    raise RuntimeError("Cluster is full!")


def request(count: int, spared: List[str] = None) -> List[str]:
  spared = spared if spared is not None else []
  crt_state = get_ns()
  avail_now = avail_now_names(crt_state)
  terminating = terminating_names(crt_state)
  if len(avail_now) >= count:
    required_subset = avail_now[:count]
    return [create_ns(name) for name in required_subset]
  else:
    missing_count = len(avail_now) - count
    if not len(terminating) >= missing_count:
      amount_needed = missing_count - len(terminating)
      destroy_namespaces_async(amount_needed, terminating, spared)
    wait_for_term(len(terminating) - missing_count)
    avail_now = avail_now_names(get_ns())
    assert len(avail_now) >= count
    return [create_ns(name) for name in avail_now]


def relinquish(*names: List[str]):
  for name in names:
    if name not in terminating_names(get_ns()):
      initiate_ns_destroy(name)


def relinquish_all():
  relinquish(*running_names(get_ns()))
