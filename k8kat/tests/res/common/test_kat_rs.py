import time
from typing import Type
from unittest.mock import patch

from k8kat.res.base.kat_res import KatRes
from k8kat.res.rs.kat_rs import KatRs
from k8kat.tests.res.base.test_kat_res import Base
from k8kat.utils.main import utils
from k8kat.utils.testing import simple_rs


class TestKatRs(Base.TestKatRes):

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatRs

  @classmethod
  def create_res(cls, name, ns=None):
    return simple_rs.create(ns=ns, name=name)

  def gen_res_with_capped_pods(self, ns, name):
    one_pod_requests = dict(memory="50M", cpu="0.25")
    one_pod_limits = dict(memory="0.1G", cpu="0.5")
    resources = dict(requests=one_pod_requests, limits=one_pod_limits)
    raw_dep = simple_rs.create(ns=ns, name=name, resources=resources)
    time.sleep(5)
    return KatRs(raw_dep)

  def gen_mock_usage_metrics(self):
    return [
      dict(containers=[dict(name='x', usage=dict(cpu='1', memory='1G'))])
    ]

