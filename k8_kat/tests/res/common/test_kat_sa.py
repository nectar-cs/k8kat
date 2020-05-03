from kubernetes.client import V1ServiceAccount, V1ObjectMeta

from k8_kat.auth.kube_broker import broker
from k8_kat.res.sa.kat_service_account import KatServiceAccount
from k8_kat.tests.res.base.test_kat_res import Base


class TestKatSa(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return broker.coreV1.create_namespaced_service_account(
      namespace=ns,
      body=V1ServiceAccount(
        metadata=V1ObjectMeta(
          name=name
        )
      )
    )

  @classmethod
  def res_class(cls):
    return KatServiceAccount

  def test_aaa_list_namespaced(self, expected=None):
    super().test_aaa_list_namespaced(
      [self.res_name, 'default']
    )

  def test_aaa_list_namespaced_filtered(self, expected=None):
    pass