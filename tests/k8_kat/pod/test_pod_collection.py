import unittest

from k8_kat.base.k8_kat import K8Kat
from tests.k8_kat.base.cluster_test import ClusterTest
from utils.testing.fixtures import test_env


def names(query=None):
  query = query or K8Kat.pods()
  return query.pluck('name')

class TestPodCollection(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestPodCollection, cls).setUpClass()
    cls.ensure_no_pods()
    test_env.create_pod('n1', 'p11', labels=dict(l1='v1'))
    test_env.create_pod('n1', 'p12', labels=dict(l2='v2'))
    test_env.create_pod('n2', 'p21', labels=dict(l1='v1'))

  def test_delete_all(self):
    self.assertCountEqual(names(), ['p11', 'p12', 'p21'])
    K8Kat.pods().lbs_inc_each(l1='v1').delete_all()
    self.assertCountEqual(names(), ['p11', 'p12', 'p21'])


if __name__ == '__main__':
  unittest.main()
