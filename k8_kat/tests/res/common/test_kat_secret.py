from kubernetes.client import V1Secret, V1ObjectMeta

from k8_kat.auth.kube_broker import broker
from k8_kat.res.secret.kat_secret import KatSecret
from k8_kat.tests.res.base.test_kat_res import Base


class TestKatSecret(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return broker.coreV1.create_namespaced_secret(
      namespace=ns,
      body=V1Secret(
        metadata=V1ObjectMeta(name=name),
        data=dict()
      )
    )

  def test_list_namespaced(self, expected=None):
    pass

  def test_aaa_list_namespaced_filtered(self, expected=None):
    pass

  @classmethod
  def res_class(cls):
    return KatSecret
