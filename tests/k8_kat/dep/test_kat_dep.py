import unittest

from k8_kat.base.k8_kat import K8Kat
from k8_kat.dep.kat_dep import KatDep
from tests.k8_kat.base.cluster_test import ClusterTest
from k8_kat.utils.testing.fixtures import test_env


class TestKatDep(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatDep, cls).setUpClass()
    test_env.create_dep(
      'n1',
      'd1',
      image='nginx',
      container='primary',
      labels=dict(l1='v1'),
      annotations={
        'commit-sha': 'sha',
        'commit-message': 'message',
        'commit-branch': 'branch',
        'commit-timestamp': 'timestamp'
      }
    )

  def test_name(self):
    kat_dep = K8Kat.deps().ns('n1').find('d1')
    self.assertEqual(kat_dep.name, 'd1')

  def test_labels(self):
    kat_dep = K8Kat.deps().ns('n1').find('d1')
    self.assertEqual(kat_dep.labels, {'app': 'd1', 'l1': 'v1'})

  def test_commit(self):
    kat_dep = K8Kat.deps().ns('n1').find('d1')
    self.assertDictEqual(kat_dep.commit, dict(
      sha='sha',
      message='message',
      branch='branch',
      timestamp='timestamp'
    ))

  def test_image_name(self):
    kat_dep = K8Kat.deps().ns('n1').find('d1')
    self.assertEqual(kat_dep.image_name, 'nginx')

  def test_container_name(self):
    kat_dep = K8Kat.deps().ns('n1').find('d1')
    self.assertEqual(kat_dep.container_name, 'primary')


if __name__ == '__main__':
  unittest.main()
