from kubernetes.client import V1Node

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.utils.main import units


class KatNode(KatRes):

  def kind(self):
    return "Node"

  @classmethod
  def is_namespaced(cls) -> bool:
    return False

  def body(self) -> V1Node:
    return self.raw

  def cpu_capacity(self) -> float:
    value = self.body().status.capacity.cpu
    return units.quant_expr_to_bytes(value)

  def mem_capacity(self) -> float:
    value = self.body().status.capacity.cpu
    return units.quant_expr_to_bytes(value)

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_node,
      list=broker.coreV1.list_node
    )

  @classmethod
  def cluster_cpu_capacity(cls) -> float:
    return sum([n.cpu_capacity for n in cls.list()])

  @classmethod
  def cluster_mem_capacity(cls) -> float:
    return sum([n.mem_capacity for n in cls.list()])
