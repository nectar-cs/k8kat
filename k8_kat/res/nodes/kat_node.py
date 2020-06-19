from functools import lru_cache
from typing import List, Optional, Dict

from kubernetes.client import V1Node

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes, MetricsDict
from k8_kat.res.pod.kat_pod import KP
from k8_kat.res.relation.relation import Relation
from k8_kat.utils.main import units, utils
from k8_kat.utils.main.class_property import classproperty


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
    value = self.body().status.capacity.get('cpu')
    return units.parse_quant_expr(value)

  def mem_capacity(self) -> float:
    value = self.body().status.capacity.get('memory')
    return units.parse_quant_expr(value)

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_node,
      list=broker.coreV1.list_node
    )

  @lru_cache(maxsize=128)
  def load_metrics(self) -> List[MetricsDict]:
    """Loads the appropriate metrics dict from k8s metrics API."""
    return broker.custom.get_cluster_custom_object(
      group='metrics.k8s.io',
      version='v1beta1',
      plural='nodes',
      name=self.name
    )

  def fetch_usage(self, resource_type: str) -> Optional[float]:
    """Fetches node's total usage for either CPU (cores) or memory (bytes).
    Overwritten at node level because there are no containers to index into.
    """
    raw_metrics_dict: List[MetricsDict] = self.load_metrics()
    if raw_metrics_dict is None:
      return None
    resource_quant = units.parse_quant_expr(
      utils.deep_get(raw_metrics_dict, 'usage', resource_type))
    return round(resource_quant, 3)

# --
# --
# --
# -------------------------------RELATIONS-------------------------------
# --
# --
# --

  def pods(self, **query) -> List[KP]:
    """Selects and returns pods associated with the node."""
    from k8_kat.res.pod.kat_pod import KatPod
    from k8_kat.res.ns.kat_ns import KatNs

    all_ns = [n.name for n in KatNs.list()]
    return sum([Relation[KatPod](
      model_class=KatPod,
      ns=ns,
      fields={"spec.nodeName": self.name},
      **query
    ) for ns in all_ns], [])