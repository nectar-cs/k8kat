import unittest

from k8_kat.res.base.k8_kat import K8Kat
from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.testing import test_env, ns_factory


class TestKatDep(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatDep, cls).setUpClass()
    cls.n1, = ns_factory.request(1)
    test_env.create_dep(
      cls.n1,
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
    kat_dep = K8Kat.deps().ns(self.n1).find('d1')
    self.assertEqual(kat_dep.name, 'd1')

  def test_labels(self):
    kat_dep = K8Kat.deps().ns(self.n1).find('d1')
    self.assertEqual(kat_dep.labels, {'app': 'd1', 'l1': 'v1'})

  def test_commit(self):
    kat_dep = K8Kat.deps().ns(self.n1).find('d1')
    self.assertDictEqual(kat_dep.commit, dict(
      sha='sha',
      message='message',
      branch='branch',
      timestamp='timestamp'
    ))

  def test_image_name(self):
    kat_dep = K8Kat.deps().ns(self.n1).find('d1')
    self.assertEqual(kat_dep.image_name, 'nginx')

  def test_container_name(self):
    kat_dep = K8Kat.deps().ns(self.n1).find('d1')
    self.assertEqual(kat_dep.container_name, 'primary')


if __name__ == '__main__':
  unittest.main()
