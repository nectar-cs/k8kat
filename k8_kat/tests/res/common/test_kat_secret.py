from kubernetes.client import V1Secret, V1ObjectMeta

from k8_kat.auth.kube_broker import broker
from k8_kat.res.secret.kat_secret import KatSecret
from k8_kat.tests.res.base.test_kat_res import Base


class TestKatSecret(Base.TestKatRes):
  def create_res(self, name, ns=None):
    return broker.coreV1.create_namespaced_secret(
      namespace=ns,
      body=V1Secret(
        metadata=V1ObjectMeta(name=name),
        data=dict()
      )
    )

  @classmethod
  def res_class(cls):
    return KatSecret