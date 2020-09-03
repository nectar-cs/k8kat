from k8kat.res.svc.kat_svc import KatSvc
from k8kat.tests.res.base.test_kat_res import Base
from k8kat.utils.testing import test_helper, ns_factory


class TestKatSvc(Base.TestKatRes):

  @classmethod
  def res_class(cls):
    return KatSvc

  @classmethod
  def create_res(cls, name, ns=None):
    return test_helper.create_svc(ns, name)

  def test_internal_ip(self):
    subject = KatSvc(self.create_res(self.res_name, self.pns))
    self.assertIsNotNone(subject.internal_ip)

  def test_from_port(self):
    subject = KatSvc(self.create_res(self.res_name, self.pns))
    self.assertEqual(subject.from_port, 80)

  def test_to_port(self):
    subject = KatSvc(self.create_res(self.res_name, self.pns))
    self.assertEqual(subject.to_port, 80)

  def test_short_dns(self):
    subject = KatSvc(self.create_res(self.res_name, self.pns))
    self.assertEqual(subject.short_dns, f'{self.res_name}.{self.pns}')

  def test_fqdn(self):
    subject = KatSvc(self.create_res(self.res_name, self.pns))
    expected = f'{self.res_name}.{self.pns}.svc.cluster.local'
    self.assertEqual(subject.fqdn, expected)
