# from k8_kat.auth.kube_broker import broker
# from k8_kat.res.ns.kat_ns import KatNs
# from k8_kat.res.svc.kat_svc import KatSvc
# from k8_kat.tests.res.base.cluster_test import ClusterTest
# from k8_kat.tests.res.base.test_kat_res import Base
# from k8_kat.utils.testing import test_helper, ns_factory
#
#
# class TestKatSvc(Base.TestKatRes):
#
#   @classmethod
#   def res_class(cls):
#     return KatNs
#
#   def create_res(self, name, ns=None):
#     broker.coreV1.create_namespace(name='foo')
#
#     return test_helper.create_svc(ns, name)
#
#