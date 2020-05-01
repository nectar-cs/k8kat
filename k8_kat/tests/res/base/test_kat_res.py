import time
from typing import Type

from k8_kat.res.base.kat_res import KatRes
from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.main import utils
from k8_kat.utils.testing import ns_factory


class Base:
  class TestKatRes(ClusterTest):

    @classmethod
    def setUpClass(cls) -> None:
      super().setUpClass()
      if cls.res_class().is_namespaced():
        cls.pns, = ns_factory.request(1)
      else:
        cls.pns = None

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

    def test_patch(self):
      self.create_res(self.res_name, self.pns)
      time.sleep(2)
      res = self.get_res()
      old_annotations = res.raw.metadata.annotations or {}
      res.raw.metadata.annotations = dict(**old_annotations, foo='bar')
      res.patch()
      from_fresh = self.get_res().raw.metadata.annotations.items()
      from_old = res.raw.metadata.annotations.items()
      self.assertTrue(('foo', 'bar') in from_fresh)
      self.assertTrue(('foo', 'bar') in from_old)

    def get_res(self) -> KatRes:
      return self.res_class().find(self.res_name, self.pns)

    def create_res(self, name, ns=None):
      raise NotImplementedError

    @classmethod
    def res_class(cls) -> Type[KatRes]:
      raise NotImplementedError
