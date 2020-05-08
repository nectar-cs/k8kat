from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils
from k8_kat.utils.testing import test_helper, simple_dep
from k8_kat.utils.testing.simple_dep import create


class TestKatDep(Base.TestKatRes):

  @classmethod
  def res_class(cls):
    return KatDep

  @classmethod
  def create_res(cls, name, ns=None):
    return test_helper.create_dep(ns, name)

  def test_image_name(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, image='busybox'))
    self.assertEqual(dep.image_name(), "busybox")

  def test_image_pull_policy(self):
    dep = KatDep(simple_dep.create(ns=self.pns, name=self.res_name, ipp='Always'))
    self.assertEqual(dep.image_pull_policy(), "Always")

  def test_pods(self):
    make = lambda: create(ns=self.pns, name=utils.rand_str(), replicas=2)
    d1, d2 = KatDep(make()), KatDep(make())

    p1, p2 = d1.pods()
    self.assertIn(d1.name, p1.name)
    self.assertIn(d1.name, p2.name)

    p1, p2 = d2.pods()
    self.assertIn(d2.name, p1.name)
    self.assertIn(d2.name, p2.name)
