from typing import Type

from kubernetes.client import V1Namespace, V1ObjectMeta

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.ns.kat_ns import KatNs
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.testing import ns_factory


class TestKatNs(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return broker.coreV1.create_namespace(
      body=V1Namespace(
        metadata=V1ObjectMeta(
          name=name
        )
      )
    )

  def setUp(self) -> None:
    super().setUp()
    KatNs.delete_if_exists(None, 'nss1', True)
    KatNs.delete_if_exists(None, 'nss2', True)

  def tearDown(self) -> None:
    super().tearDown()
    KatNs.delete_if_exists(None, 'nss1', False)
    KatNs.delete_if_exists(None, 'nss2', False)

  def test_list(self):
    self.create_res('nss1')
    self.create_res('nss2')
    result = KatNs.list()
    result_names = [kns.name for kns in result]
    self.assertIn('nss1', result_names)
    self.assertIn('nss2', result_names)

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatNs

  def test_patch(self):
    pass

  def test_init(self):
    pass

  def test_delete_and_wait(self):
    pass

  def test_find(self):
    pass

  def test_delete_without_wait(self):
    pass
