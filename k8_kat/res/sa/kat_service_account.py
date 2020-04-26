from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes


class KatServiceAccount(KatRes):

  @property
  def kind(self):
    return "ServiceAccount"

  @classmethod
  def _api_methods(cls):
    return(
      dict(
        read=broker.coreV1.read_namespaced_service_account,
        delete=broker.coreV1.delete_namespaced_service_account,
      )
    )

  @classmethod
  def _collection_class(cls):
    pass
