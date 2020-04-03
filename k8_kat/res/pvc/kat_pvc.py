from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes


class KatPvc(KatRes):

  @property
  def kind(self):
    return "PersistentVolumeClaim"

  @classmethod
  def _find(cls, ns, name):
    return broker.coreV1.read_namespaced_persistent_volume_claim(
      namespace=ns,
      name=name
    )

  @classmethod
  def _collection_class(cls):
    from k8_kat.res.pvc.pvc_collection import PvcCollection
    return PvcCollection()

  def _perform_patch_self(self):
    broker.coreV1.patch_namespaced_persistent_volume_claim(
      name=self.name,
      namespace=self.namespace,
      body=self.raw
    )
