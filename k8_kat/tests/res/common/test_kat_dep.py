from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils
from k8_kat.utils.testing import simple_dep
from k8_kat.utils.testing.simple_dep import create


class TestKatDep(Base.TestKatRes):

  @classmethod
  def res_class(cls):
    return KatDep

  @classmethod
  def create_res(cls, name, ns=None):
    return simple_dep.create(ns=ns, name=name)

  def test_annotate(self,  wait_sec=2):
    pass

  def test_image_name(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, image='busybox'))
    self.assertEqual(dep.image_name(), "busybox")

  def test_image_pull_policy(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, ipp='Always'))
    self.assertEqual(dep.ipp(), "Always")

  def test_ternary_state(self):
    pass

  def test_ternary_state_positive(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, replicas=2))
    self.assertEqual(dep.ternary_status(), 'pending')
    dep.wait_until(dep.is_running_normally)
    self.assertEqual(dep.ternary_status(), 'positive')

  def test_ternary_state_negative(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, image='bro-ken'))
    self.assertEqual(dep.ternary_status(), 'pending')
    dep.wait_until(dep.has_settled)
    self.assertEqual(dep.ternary_status(), 'negative')

  def test_pods(self):
    def make():
      dep = KatDep(create(ns=self.pns, name=utils.rand_str(), replicas=2))
      return dep.wait_until(dep.is_running_normally) and dep

    d1, d2 = make(), make()

    p1, p2 = d1.pods()
    self.assertIn(d1.name, p1.name)
    self.assertIn(d1.name, p2.name)

    p1, p2 = d2.pods()
    self.assertIn(d2.name, p1.name)
    self.assertIn(d2.name, p2.name)

  def gen_res_with_capped_pods(self, ns, name):
    one_pod_requests = dict(memory="25M", cpu="0.125")
    one_pod_limits = dict(memory="0.05G", cpu="0.25")
    resources = dict(requests=one_pod_requests, limits=one_pod_limits)
    raw_dep = simple_dep.create(ns=ns, name=name, replicas=2, resources=resources)
    return KatDep(raw_dep)

  def gen_mock_usage_metrics(self):
    return [
      dict(containers=[
        dict(name='x', usage=dict(cpu='250m', memory='0.25G')),
        dict(name='y', usage=dict(cpu='0.25', memory='750M'))
      ]),
      dict(containers=[
        dict(name='x', usage=dict(cpu='500m', memory=None)),
        dict(name='y', usage=dict(memory=None))
      ])
    ]

