from functools import lru_cache
from typing import List

from kubernetes.client import V1Namespace

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes, MetricsDict
from k8kat.res.pod.kat_pod import KP
from k8kat.res.relation.relation import Relation
from k8kat.res.sa.kat_service_account import KatServiceAccount
from k8kat.utils.main.class_property import classproperty


class KatNs(KatRes):

  @classproperty
  def kind(self):
    return "Namespace"

# --
# --
# --
# -------------------------------INTEL-------------------------------
# --
# --
# --

  def _perform_delete_self(self):
    broker.coreV1.delete_namespace(self.name)

  def is_active(self) -> bool:
    if self.raw.status:
      return self.raw.status.phase == 'Active'
    else:
      return False

  def is_work_ready(self) -> bool:
    if self.is_active():
      default_sa = KatServiceAccount.find('default', self.name)
      if default_sa:
        if len(default_sa.secrets()) == 1:
          return None not in default_sa.secrets()
    return False

  @lru_cache(maxsize=128)
  def load_per_pod_metrics(self) -> List[MetricsDict]:
    """Loads the appropriate metrics dict from k8s metrics API."""
    return broker.custom.list_namespaced_custom_object(
      group='metrics.k8s.io',
      version='v1beta1',
      namespace=self.name,
      plural='pods'
    )['items']

# --
# --
# --
# -------------------------------PLUMBING-------------------------------
# --
# --
# --

  def body(self) -> V1Namespace:
    return self.raw

  @classmethod
  def is_namespaced(cls) -> bool:
    return False

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_namespace,
      list=broker.coreV1.list_namespace,
      patch=broker.coreV1.patch_namespace,
      delete=broker.coreV1.delete_namespace
    )

# --
# --
# --
# -------------------------------RELATIONS-------------------------------
# --
# --
# --

  def pods(self, **query) -> List[KP]:
    """Selects and returns pods associated with the namespace."""
    from k8kat.res.pod.kat_pod import KatPod
    return Relation[KatPod](
      model_class=KatPod,
      ns=self.name,
      **query
    )
