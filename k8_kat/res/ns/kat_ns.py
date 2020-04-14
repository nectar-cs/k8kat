from typing import Dict

from kubernetes.client.rest import ApiException

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes


class KatNs(KatRes):

  @classmethod
  def find(cls, ns, name=None):
    try:
      return cls(cls._find(ns, name))
    except ApiException:
      return None

  @classmethod
  def _find(cls, ns, name):
    _id = ns or name
    return broker.coreV1.read_namespace(name=_id)

  def _delete(self):
    broker.coreV1.delete_namespace(self.name)

  @classmethod
  def _collection_class(cls):
    pass

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    pass