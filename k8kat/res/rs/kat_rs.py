from functools import lru_cache
from typing import Dict, List

from kubernetes.client import V1ReplicaSet

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes, MetricsDict
from k8kat.res.base.label_set_expressions import label_conditions_to_expr
from k8kat.res.pod.kat_pod import KP
from k8kat.res.relation.relation import Relation
from k8kat.utils.main.class_property import classproperty


class KatRs(KatRes):

  @classproperty
  def kind(self):
    return "ReplicaSet"

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    return self.raw.spec.selector.match_labels or {}

# --
# --
# --
# -------------------------------INTEL-------------------------------
# --
# --
# --

  @lru_cache(maxsize=128)
  def load_per_pod_metrics(self) -> List[MetricsDict]:
    """Loads the appropriate metrics dict from k8s metrics API."""
    return broker.custom.list_namespaced_custom_object(
      group='metrics.k8s.io',
      version='v1beta1',
      namespace=self.namespace,
      label_selector=label_conditions_to_expr(self.pod_select_labels.items(), []),
      plural='pods'
    )['items']

# # --
# # --
# # --
# # -------------------------------ACTION-------------------------------
# # --
# # --
# # --

  def body(self) -> V1ReplicaSet:
    return self.raw

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.appsV1.read_namespaced_replica_set,
      patch=broker.appsV1.patch_namespaced_replica_set,
      delete=broker.appsV1.delete_namespaced_replica_set,
      list=broker.appsV1.list_namespaced_replica_set
    )

# --
# --
# --
# -------------------------------RELATIONS-------------------------------
# --
# --
# --

  def pods(self, **query) -> List[KP]:
    """Selects and returns pods associated with the replica set."""
    from k8kat.res.pod.kat_pod import KatPod
    return Relation[KatPod](
      model_class=KatPod,
      ns=self.ns,
      labels=self.pod_select_labels,
      **query
    )

