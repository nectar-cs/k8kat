from kubernetes.client import V1Secret

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes


class KatSecret(KatRes):

  def raw_ob(self) -> V1Secret:
    return self.raw

  @property
  def kind(self):
    return "Secret"

  @classmethod
  def _api_methods(cls):
    return(
      dict(
        read=broker.coreV1.read_namespaced_secret,
        delete=broker.coreV1.delete_namespaced_secret,
      )
    )

