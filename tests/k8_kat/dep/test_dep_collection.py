import unittest

from k8_kat.base.k8_kat import K8Kat
from tests.k8_kat.base.cluster_test import ClusterTest
from utils.testing.fixtures.test_env import TestEnv


class TestDepCollection(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestDepCollection, cls).setUpClass()
    TestEnv.create_dep('n1', 'd11', labels=[('c', 'c'), ('l1', 'v1')])
    TestEnv.create_dep('n1', 'd12', labels=[('c', 'c'), ('l1', 'v2')])

    TestEnv.create_dep('n2', 'd21', labels=[('l1', 'v1')])
    TestEnv.create_dep('n2', 'd22', labels=[('l2', 'v2')])

  def test_names(self):
    result = K8Kat.deps().names('d11').go()
    self.assertEqual([dep.name for dep in result], ['d11'])

    result = K8Kat.deps().names('d11', 'd12').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    result = K8Kat.deps().names('d11', 'd22').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd22'])

    result = K8Kat.deps().names('d11', 'd22').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd22'])

  def test_lbs_inc_each(self):
    pass
    result = K8Kat.deps().ns(['n1']).lbs_inc_each(l1='v1').go()
    self.assertCountEqual([dep.name for dep in result], ['d11'])

    result = K8Kat.deps().ns('n1').lbs_inc_each([('c', 'c')]).go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    result = K8Kat.deps().ns('n1', 'n2').lbs_inc_each(l1='v1').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd21'])

    q = [('l1', 'v1'), ('c', 'c')]
    result = K8Kat.deps().ns('n1', 'n2').lbs_inc_each(q).go()
    self.assertCountEqual([dep.name for dep in result], ['d11'])

    result = K8Kat.deps().ns('n1', 'n2').lbs_inc_each(c='c').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    q = [('x', 'y'), ('c', 'c')]
    result = K8Kat.deps().ns('n1', 'n2').lbs_inc_each(q).go()
    self.assertCountEqual([dep.name for dep in result], [])

  def test_lbs_inc_any(self):
    result = K8Kat.deps().ns('n1').lbs_inc_any(c='c', l1='v1').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12'])

    result = K8Kat.deps().ns('n1', 'n2').lbs_inc_any(c='c', l1='v1').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd12', 'd21'])

    q = K8Kat.deps().ns('n1', 'n2').lbs_inc_any(c='c', l1='v1')
    result = q.lbs_inc_each(l1='v1').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd21'])

    q = K8Kat.deps().ns('n1', 'n2').lbs_inc_each(l1='v1')
    result = q.lbs_inc_any(c='c', l1='v1').go()
    self.assertCountEqual([dep.name for dep in result], ['d11', 'd21'])


if __name__ == '__main__':
    unittest.main()
