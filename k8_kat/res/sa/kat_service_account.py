from typing import List

from kubernetes.client import V1ServiceAccount

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes


class KatServiceAccount(KatRes):

  def raw_ob(self) -> V1ServiceAccount:
    return self.raw

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

  def secrets(self) -> List[any]:
    from k8_kat.res.secret.kat_secret import KatSecret
    make = lambda sd: KatSecret.find(sd.namespace or self.ns, sd.name)
    secret_descriptors = self.raw_ob().secrets or []
    return [make(secret_desc) for secret_desc in secret_descriptors]

  @classmethod
  def _collection_class(cls):
    pass
