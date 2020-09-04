from kubernetes.client import V1Node

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main import units
from k8kat.utils.main.class_property import classproperty


class KatNode(KatRes):

  @classproperty
  def kind(self):
    return "Node"

  @classmethod
  def is_namespaced(cls) -> bool:
    return False

# --
# --
# --
# -------------------------------INTEL-------------------------------
# --
# --
# --

  def body(self) -> V1Node:
    return self.raw

  def cpu_capacity(self) -> float:
    quant_expr = self.body().status.capacity.get('cpu')
    return units.parse_quant_expr(quant_expr) if quant_expr else None

  def mem_capacity(self) -> float:
    quant_expr = self.body().status.capacity.get('memory')
    return units.parse_quant_expr(quant_expr) if quant_expr else None

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_node,
      list=broker.coreV1.list_node
    )
