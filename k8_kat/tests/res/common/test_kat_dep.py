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
    make = lambda: create(ns=self.pns, name=utils.rand_str(), replicas=2)
    d1, d2 = KatDep(make()), KatDep(make())

    p1, p2 = d1.pods()
    self.assertIn(d1.name, p1.name)
    self.assertIn(d1.name, p2.name)

    p1, p2 = d2.pods()
    self.assertIn(d2.name, p1.name)
    self.assertIn(d2.name, p2.name)
