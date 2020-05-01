from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes


class KatPvc(KatRes):

  @property
  def kind(self):
    return "PersistentVolumeClaim"

  @classmethod
  def _api_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_persistent_volume_claim,
      patch=broker.coreV1.patch_namespaced_persistent_volume_claim,
      delete=broker.coreV1.delete_namespaced_persistent_volume_claim
    )
