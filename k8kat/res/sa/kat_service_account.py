from typing import List

from kubernetes.client import V1ServiceAccount

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main.class_property import classproperty


class KatServiceAccount(KatRes):

  @classproperty
  def kind(self):
    return "ServiceAccount"

  def body(self) -> V1ServiceAccount:
    return self.raw

  @classmethod
  def list_excluding_sys(cls, ns=None, **query):
    updated_query = dict(
      **query,
      not_fields={
        **(query.get('not_fields', {})),
        'metadata.name': 'default',
      }
    )
    return cls.list(ns, **updated_query)

  @classmethod
  def k8s_verb_methods(cls):
    return (
      dict(
        read=broker.coreV1.read_namespaced_service_account,
        patch=broker.coreV1.patch_namespaced_service_account,
        delete=broker.coreV1.delete_namespaced_service_account,
        list=broker.coreV1.list_namespaced_service_account,
      )
    )

  def secrets(self) -> List[any]:
    from k8kat.res.secret.kat_secret import KatSecret
    make = lambda sd: KatSecret.find(sd.name, sd.namespace or self.ns)
    secret_descriptors = self.body().secrets or []
    return [make(secret_desc) for secret_desc in secret_descriptors]
