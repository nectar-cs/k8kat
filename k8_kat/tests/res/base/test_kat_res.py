import time
from typing import Type, List
from unittest.mock import patch

from k8_kat.res.base.kat_res import KatRes
from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.main import utils
from k8_kat.utils.testing import ns_factory


class Base:
  class TestKatRes(ClusterTest):

    @classmethod
    def setUpClass(cls) -> None:
      super().setUpClass()
      cls.pns, cls.pns2 = None, None
      if cls.res_class().is_namespaced():
        cls.pns, cls.pns2 = ns_factory.request(2)

    def setUp(self) -> None:
      self.res_name = utils.rand_str(8)

    def tearDown(self) -> None:
      super().tearDown()
      if not self.res_class().is_namespaced():
        instance = self.get_res()
        if instance:
          instance.delete(wait_until_gone=True)
          
    def test_init(self):
      body = self.create_res(self.res_name, self.pns)
      res = self.res_class()(body)
      self.assertIsInstance(res, self.res_class())
      self.assertEqual(res.raw.metadata.name, self.res_name)
      self.assertEqual(res.raw.kind, res.kind)

    def test_find(self):
      self.create_res(self.res_name, self.pns)
      res = self.get_res()
      self.assertIsNotNone(res)
      self.assertIsInstance(res, self.res_class())
      self.assertEqual(res.raw.metadata.name, self.res_name)
      self.assertEqual(res.raw.kind, res.kind)

    def test_inflate(self):
      raw_res = self.create_res(self.res_name, self.pns)
      kat_instance = KatRes.inflate(raw_res)
      self.assertIsNotNone(kat_instance)
      self.assertIsInstance(kat_instance, self.res_class())

    def test_list_namespaced(self, expected=None):
      if self.res_class().is_namespaced():
        ns, = ns_factory.request(1)
        self.create_res(self.res_name, ns)
        self.create_res(self.res_name, self.pns)
        result = self.res_class().list(ns=ns)
        expected = expected or [self.res_name]
        self.assertEqual(sorted(names(result)), sorted(expected))

    def test_list_namespaced_label_filters(self):
      if self.res_class().is_namespaced():
        ns, = ns_factory.request(1)
        right = self.res_class()(self.create_res(utils.rand_str(), ns))
        wrong = self.res_class()(self.create_res(utils.rand_str(), ns))

        right.wait_until(right.has_settled)
        wrong.wait_until(wrong.has_settled)

        time.sleep(2)

        right.label(foo='bar')
        wrong.label(foo='baz')

        label_query = dict(foo='bar')
        result = self.res_class().list(ns=ns, labels=label_query)
        self.assertEqual(sorted(names(result)), sorted([right.name]))

        field_query = {'metadata.name': right.name}
        result = self.res_class().list(ns=ns, fields=field_query)
        self.assertEqual(sorted(names(result)), sorted([right.name]))

    def test_reload_when_exists(self):
      self.create_res(self.res_name, self.pns)
      res = self.get_res()
      res.reload()

    def test_delete_without_wait(self):
      self.create_res(self.res_name, self.pns)
      res = self.get_res()
      if hasattr(res.raw, 'status'):
        if hasattr(res.raw.status, 'phase'):
          old_phase = res.raw.status.phase
          self.get_res().delete(wait_until_gone=False)
          self.assertIsNot(self.get_res(), old_phase)

    def test_delete_and_wait(self):
      self.create_res(self.res_name, self.pns)
      self.get_res().delete(wait_until_gone=True)
      self.assertIsNone(self.get_res())

    def test_annotate(self):
      res = self.res_class()(self.create_res(self.res_name, self.pns))
      res.wait_until(res.has_settled)
      self.assertNotIn(('foo', 'bar'), res.annotations.items())
      res.annotate(foo='bar')
      self.assertIn(('foo', 'bar'), res.reload().annotations.items())

    def test_ternary_state(self):
      res = self.res_class()(self.create_res(self.res_name, self.pns))
      self.assertEqual(res.ternary_status(), 'positive')

    def gen_mock_metrics(self):
      """Subclasses must return 1 CPU core Core and 1GB mem"""
      return None

    def test_mem_and_cpu_used(self):
      if self.gen_mock_metrics():
        res = self.res_class()(self.create_res(self.res_name, self.pns))
        with patch.object(self.res_class(), 'load_metrics') as mocked_metrics:
          mocked_metrics.return_value = self.gen_mock_metrics()
          self.assertEqual(res.mem_used(), 1_000_000_000)
          self.assertEqual(res.cpu_used(), 1)

    def get_res(self) -> KatRes:
      return self.res_class().find(self.res_name, self.pns)

    @classmethod
    def create_res(cls, name, ns=None):
      raise NotImplementedError

    @classmethod
    def res_class(cls) -> Type[KatRes]:
      raise NotImplementedError


def names(res_list) -> List[str]:
  return [r.name for r in res_list]
