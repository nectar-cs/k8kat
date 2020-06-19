from typing import Type
from unittest.mock import patch

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.nodes.kat_node import KatNode
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils, units
from k8_kat.utils.testing import simple_pod


class TestKatNode(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return cls.first_node()

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatNode

  def tearDown(self) -> None:
    pass

  def get_res(self) -> KatRes:
    return KatNode(self.first_node())

  def test_init(self):
    pass

  def test_find(self):
    self.assertIsNotNone(self.first_node())

  def test_delete_and_wait(self):
    pass

  def test_annotate(self):
    pass

  def test_inflate(self):
    pass

  def test_delete_without_wait(self):
    pass

  @staticmethod
  def first_node():
    return broker.coreV1.list_node().items[0]

  def test_pods(self):
    n1 = KatNode(self.create_res('node'))
    simple_pod.create(ns="default", name=utils.rand_str())

    pods = n1.pods()
    for p in pods:
      self.assertEqual(p.body().spec.node_name, n1.body().metadata.name)

  def test_load_metrics(self):
    n1 = KatNode(self.create_res('node'))

    with patch(f"{KatNode.__module__}.broker.custom.get_cluster_custom_object") as mocked_get:
      mocked_get.return_value = ["test value"]
      self.assertEqual(n1.load_metrics(), ["test value"])
      self.assertEqual(mocked_get.call_count, 1)

  def test_fetch_usage(self):
    n1 = KatNode(self.create_res('node'))
    with patch(
        f"{KatNode.__module__}.{KatNode.__name__}.load_metrics") as mocked_metrics:
      mocked_metrics.return_value = {'usage': {'cpu': '3910299n', 'memory': '17604Ki'}}

      self.assertEqual(n1.fetch_usage('cpu'),
                       round(units.parse_quant_expr('3910299n'), 3))
      self.assertEqual(n1.fetch_usage('memory'),
                       round(units.parse_quant_expr('17604Ki'), 3))

      self.assertEqual(mocked_metrics.call_count, 2)

  def test_fetch_usage_with_undefined(self):
    n1 = KatNode(self.create_res('node'))
    with patch(
        f"{KatNode.__module__}.{KatNode.__name__}.load_metrics") as mocked_metrics:
      mocked_metrics.return_value = None

      self.assertEqual(n1.fetch_usage('cpu'), None)
      self.assertEqual(n1.fetch_usage('memory'), None)

      self.assertEqual(mocked_metrics.call_count, 2)