from kubernetes.client import V1Secret

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.utils.main.class_property import classproperty


class KatSecret(KatRes):

  def raw_ob(self) -> V1Secret:
    return self.raw

  @classproperty
  def kind(self):
    return "Secret"

  @classmethod
  def k8s_verb_methods(cls):
    return(
      dict(
        read=broker.coreV1.read_namespaced_secret,
        patch=broker.coreV1.patch_namespaced_secret,
        delete=broker.coreV1.delete_namespaced_secret,
        list=broker.coreV1.list_namespaced_secret,
      )
    )
