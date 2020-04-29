from kubernetes.client.rest import ApiException

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.sa.kat_service_account import KatServiceAccount


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

  def is_active(self) -> bool:
    if self.raw.status:
      return self.raw.status.phase == 'Active'
    else:
      return False

  def is_work_ready(self) -> bool:
    if self.is_active():
      default_sa = KatServiceAccount.find(self.name, 'default')
      if default_sa:
        if len(default_sa.secrets()) == 1:
          return None not in default_sa.secrets()
    return False

  @classmethod
  def _collection_class(cls):
    pass
