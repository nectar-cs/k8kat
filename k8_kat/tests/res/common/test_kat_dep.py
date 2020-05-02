from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.testing import test_helper, simple_dep


class TestKatDep(Base.TestKatRes):

  @classmethod
  def res_class(cls):
    return KatDep

  def create_res(self, name, ns=None):
    return test_helper.create_dep(ns, name)

  def test_image_name(self):
    dep = KatDep(simple_dep.create(
      ns=self.pns,
      name=self.res_name,
      image='busybox'
    ))
    self.assertEqual(dep.image_name(), "busybox")

  def test_image_pull_policy(self):
    dep = KatDep(simple_dep.create(
      ns=self.pns,
      name=self.res_name,
      ipp='Always'
    ))
    self.assertEqual(dep.image_pull_policy(), "Always")
