from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.testing import ns_factory, test_helper


class TestKatDep(Base.TestKatRes):

  @classmethod
  def res_class(cls):
    return KatDep

  def create_res(self, name, ns=None):
    return test_helper.create_dep(ns, name)
