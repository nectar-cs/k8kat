from kubernetes.client import V1ResourceQuota

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.utils.main.class_property import classproperty


class KatQuota(KatRes):

  @classproperty
  def kind(self):
    return "ResourceQuota"

  def body(self) -> V1ResourceQuota:
    return self.raw

  def cpu_used(self):
    body = self.body()
    body.spec.hard.get('cpu')
    pass

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_resource_quota,
      patch=broker.coreV1.patch_namespaced_resource_quota,
      delete=broker.coreV1.delete_namespaced_resource_quota,
      list=broker.coreV1.list_namespaced_resource_quota
    )

