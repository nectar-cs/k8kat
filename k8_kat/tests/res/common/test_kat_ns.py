import time
from typing import Type
from unittest.mock import patch

from kubernetes.client import V1Namespace, V1ObjectMeta

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.ns.kat_ns import KatNs
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils
from k8_kat.utils.testing import simple_pod


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

  # @classmethod
  # def create_namespaced_res(cls, name, ns):
  #   return simple_pod.create(name=name, ns=ns)

  def setUp(self) -> None:
    super().setUp()
    KatNs.delete_if_exists(None, 'nss1', True)
    KatNs.delete_if_exists(None, 'nss2', True)

  def tearDown(self) -> None:
    super().tearDown()
    KatNs.delete_if_exists(None, 'nss1', True)
    KatNs.delete_if_exists(None, 'nss2', True)

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

  def test_pods(self):
    n1 = KatNs(self.create_res('nss1'))
    n2 = KatNs(self.create_res('nss2'))

    n1.wait_until(n1.is_work_ready)
    n2.wait_until(n2.is_work_ready)

    simple_pod.create(ns="nss1", name=utils.rand_str())
    simple_pod.create(ns="nss2", name=utils.rand_str())

    p1 = n1.pods()
    p2 = n2.pods()

    for p in p1:
      self.assertEqual(p.ns, n1.body().metadata.name)
    for p in p2:
      self.assertEqual(p.ns, n2.body().metadata.name)

  def test_load_metrics(self):
    n1 = KatNs(self.create_res('nss1'))
    n1.wait_until(n1.is_work_ready)
    simple_pod.create(ns="nss1", name=utils.rand_str())

    with patch(f"{KatNs.__module__}.broker.custom.list_namespaced_custom_object") as mocked_get:
      mocked_get.return_value = {"items": ["test value"]}
      self.assertEqual(n1.load_metrics(), ["test value"])
      self.assertEqual(mocked_get.call_count, 1)