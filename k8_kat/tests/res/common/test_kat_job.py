import time
from typing import Type

from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.job.kat_job import KatJob
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils
from k8_kat.utils.testing import simple_job


class TestKatJob(Base.TestKatRes):

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatJob

  @classmethod
  def create_res(cls, name, ns=None):
    return simple_job.create(ns=ns, name=name)

  def test_pods(self):
    make = lambda: simple_job.create(ns=self.pns, name=utils.rand_str())
    r1, r2 = KatJob(make()), KatJob(make())

    time.sleep(5)

    p1 = r1.pods()[0]
    p1.wait_until(p1.is_running_normally)
    self.assertIn(r1.name, p1.name)

    p2 = r2.pods()[0]
    p2.wait_until(p2.is_running_normally)
    self.assertIn(r2.name, p2.name)

  def gen_mock_usage_metrics(self):
    return [
      dict(containers=[
        dict(name='x', usage=dict(cpu='500m', memory='.25G')),
        dict(name='y', usage=dict(cpu='0.5', memory='750M'))
      ]),
      dict(containers=[
        dict(name='x', usage=dict(cpu='0m', memory=None)),
        dict(name='y', usage=dict(memory=None))
      ])
    ]
