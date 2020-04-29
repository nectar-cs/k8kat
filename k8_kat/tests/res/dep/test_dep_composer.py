import unittest

from k8_kat.res.base.k8_kat import K8Kat
from k8_kat.res.dep.dep_composer import DepComposer
from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.main import utils
from k8_kat.utils.testing import test_env, ns_factory

subject = DepComposer

class TestDepComposer(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestDepComposer, cls).setUpClass()
    cls.n1, cls.n2 = ns_factory.request(2)
    test_env.create_dep(cls.n1, 'd0', replicas=1)
    test_env.create_dep(cls.n1, 'd11', replicas=1)
    test_env.create_dep(cls.n1, 'd12', replicas=1)
    test_env.create_dep(cls.n2, 'd21', replicas=1)

    test_env.create_svc(cls.n1, 'd11')
    test_env.create_svc(cls.n2, 'd21')

  @staticmethod
  def the_svc_names(deps):
    subject.associate_svcs(deps)
    flat_svcs = utils.flatten([dep.svcs() for dep in deps])
    return sorted([svc.name for svc in flat_svcs])

  @staticmethod
  def the_pod_app_lbs(deps):
    subject.associate_pods(deps)
    flat_pods = utils.flatten([dep.pods() for dep in deps])
    return sorted([pod.label('app') for pod in flat_pods])

  def test_associate_svcs(self):
    deps = K8Kat.deps().names('d0').go()
    self.assertEqual(self.the_svc_names(deps), [])

    deps = K8Kat.deps().names('d11').go()
    self.assertEqual(self.the_svc_names(deps), ['d11'])

    deps = K8Kat.deps().names('d11', 'd12').go()
    self.assertEqual(self.the_svc_names(deps), ['d11'])

    deps = K8Kat.deps().ns(self.n1, self.n2).go()
    self.assertEqual(self.the_svc_names(deps), sorted(['d11', 'd21']))

  def test_associate_pods(self):
    deps = K8Kat.deps().ns(self.n1).names('d11').go()
    self.assertEqual(self.the_pod_app_lbs(deps), ['d11'])

    deps = K8Kat.deps().ns(self.n1, self.n2).go()
    self.assertEqual(self.the_pod_app_lbs(deps), sorted(['d0', 'd11', 'd12', 'd21']))


if __name__ == '__main__':
    unittest.main()
