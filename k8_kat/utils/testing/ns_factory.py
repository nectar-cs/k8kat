import time
from threading import Thread
from typing import Tuple, List

from kubernetes.client import V1Namespace, V1ObjectMeta

from k8_kat.auth.kube_broker import broker

config = dict(
  max_ns=10
)

def possible_names():
  return [make_name(i) for i in range(max_ns())]


def max_ns() -> int:
  return config['max_ns']


def make_name(index: int) -> str:
  return f"ns{index + 1}"


def create_ns(name) -> V1Namespace:
  return broker.coreV1.create_namespace(
    body=V1Namespace(metadata=V1ObjectMeta(name=name))
  )


def get_ns() -> List[Tuple[str, str]]:
  api = broker.coreV1
  simplified = lambda n: (n.metadata.name, n.status.phase)
  return [simplified(ns) for ns in api.list_namespace().items]


def avail_now_names(crt_list) -> List[str]:
  crt_names = [ns[0] for ns in crt_list]
  return list(set(possible_names()) - set(crt_names))


def terminating_names(crt_list) -> List[str]:
  return [ns[0] for ns in crt_list if ns[1] == 'Terminating']


def wait_for_term(wait_for_n: int):
  print(f"Waiting for {wait_for_n} namespaces to finish being destroyed...")
  while len(avail_now_names(get_ns())) < wait_for_n:
    time.sleep(1)


def destroy_ns(name):
  print(f"Starting {name} destruction")
  broker.coreV1.delete_namespace(name)
  print(f"Finished {name} destruction")


def initiate_ns_destroy(name):
  Thread(target=destroy_ns, args=(name,)).start()


def destroy_namespaces_async(terminating, count, spared: List[str]):
  victim_names = set(possible_names()) - set(terminating) - set(spared)

  if victim_names >= count:
    victim_names = victim_names[:count]
    print(f"Enough non-terminating ns to destroy: {victim_names}")
    for victim_name in victim_names:
      initiate_ns_destroy(victim_name)
  else:
    raise RuntimeError("Cluster is full!")


def request(count: int, spared: List[str]):
  crt_state = get_ns()
  avail_now = avail_now_names(crt_state)
  terminating = terminating_names(crt_state)
  if len(avail_now) >= count:
    return [create_ns(name).metadata.name for name in avail_now]
  else:
    missing_count = len(avail_now) - count
    print(f"Too few avail: {count} < {len(avail_now)}. Need {missing_count}.")
    if not len(terminating) >= missing_count:
      amount_needed = missing_count - len(terminating)
      destroy_namespaces_async(amount_needed, terminating, spared)
    wait_for_term(len(terminating) - missing_count)
    avail_now = avail_now_names(get_ns())
    print(f"Wait finished, delivering: {avail_now}")
    assert len(avail_now) >= count
    return [create_ns(name).metadata.name for name in avail_now]

def relinquish(names: List[str]):
  for name in names:
    initiate_ns_destroy(name)
