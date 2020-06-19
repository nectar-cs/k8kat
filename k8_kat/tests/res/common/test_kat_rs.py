import time
from typing import Type
from unittest.mock import patch

from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.rs.kat_rs import KatRs
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils
from k8_kat.utils.testing import simple_rs


class TestKatRs(Base.TestKatRes):

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatRs

  @classmethod
  def create_res(cls, name, ns=None):
    return simple_rs.create(ns=ns, name=name, labels={"simple": "test"})

  def test_pods(self):
    make = lambda: simple_rs.create(ns=self.pns, name=utils.rand_str(), labels={"simple": "test"}, replicas=2)
    r1, r2 = KatRs(make()), KatRs(make())

    time.sleep(5)

    p1, p2 = r1.pods()
    p1.wait_until(p1.is_running_normally)
    p2.wait_until(p2.is_running_normally)
    self.assertIn(r1.name, p1.name)
    self.assertIn(r1.name, p2.name)

    p1, p2 = r2.pods()
    p1.wait_until(p1.is_running_normally)
    p2.wait_until(p2.is_running_normally)
    self.assertIn(r2.name, p1.name)
    self.assertIn(r2.name, p2.name)

  def test_load_metrics(self):
    make = lambda: simple_rs.create(ns=self.pns, name=utils.rand_str(), labels={"simple": "test"}, replicas=2)
    r1, r2 = KatRs(make()), KatRs(make())

    with patch(f"{KatRs.__module__}.broker.custom.list_namespaced_custom_object") as mocked_get:
      mocked_get.return_value = {"items": ["test value"]}
      self.assertEqual(r1.load_metrics(), ["test value"])
      self.assertEqual(mocked_get.call_count, 1)