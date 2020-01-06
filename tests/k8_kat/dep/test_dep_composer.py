import unittest

from k8_kat.base.k8_kat import K8Kat
from k8_kat.dep.dep_composer import DepComposer
from tests.k8_kat.base.k8_kat_test import ClusterTest
from utils.main.utils import Utils

subject = DepComposer

class TestDepComposer(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestDepComposer, cls).setUpClass()
    cls.create_dep('n1', 'd0')
    cls.create_dep('n1', 'd11')
    cls.create_dep('n1', 'd12')
    cls.create_dep('n2', 'd21')

    cls.create_dep_svc('n1', 'd11')
    cls.create_dep_svc('n2', 'd21')

  @staticmethod
  def the_svc_names(deps):
    subject.associate_svcs(deps)
    flat_svcs = Utils.flatten([dep.svcs() for dep in deps])
    return [svc.name for svc in flat_svcs]

  @staticmethod
  def the_pod_app_lbs(deps):
    subject.associate_pods(deps)
    flat_pods = Utils.flatten([dep.pods() for dep in deps])
    return [pod.label('app') for pod in flat_pods]

  def test_associate_svcs(self):
    deps = K8Kat.deps().names('d0').go()
    self.assertEqual(self.the_svc_names(deps), [])

    deps = K8Kat.deps().names('d11').go()
    self.assertEqual(self.the_svc_names(deps), ['d11'])

    deps = K8Kat.deps().names('d11', 'd12').go()
    self.assertEqual(self.the_svc_names(deps), ['d11'])

    deps = K8Kat.deps().ns('n1', 'n2').go()
    self.assertEqual(self.the_svc_names(deps), ['d11', 'd21'])

  def test_associate_pods(self):
    deps = K8Kat.deps().names('d11').go()
    self.assertEqual(self.the_pod_app_lbs(deps), ['d11'])

    deps = K8Kat.deps().ns('n1', 'n2').go()
    self.assertEqual(self.the_pod_app_lbs(deps), ['d0', 'd11', 'd12', 'd21'])


if __name__ == '__main__':
    unittest.main()
