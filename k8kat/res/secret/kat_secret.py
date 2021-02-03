import base64
from typing import Dict

from kubernetes.client import V1Secret

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main.class_property import classproperty


class KatSecret(KatRes):

  def raw_ob(self) -> V1Secret:
    return self.raw

  @classproperty
  def kind(self):
    return "Secret"

  def decoded_data(self) -> Dict:
    def dec(enc_str: str) -> str:
      message_bytes = base64.b64decode(enc_str.encode('ascii'))
      return message_bytes.decode('ascii')

    encoded_data: Dict = self.raw_ob().data or {}
    return {k: dec(v) for k, v in encoded_data.items()}

  @classmethod
  def list_excluding_sys(cls, ns=None, **query):
    updated_query = dict(
      **query,
      not_fields={
        **(query.get('not_fields', {})),
        'type': 'kubernetes.io/service-account-token'
      }
    )
    return cls.list(ns, **updated_query)

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
