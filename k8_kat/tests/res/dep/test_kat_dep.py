from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.testing import ns_factory, test_helper


class TestKatDep(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatDep, cls).setUpClass()
    cls.n1, = ns_factory.request(1)
    create_dep(cls.n1)

  def dep(self):
    return KatDep.find(, 'd1', self.n1

  def test_name(self):
    self.assertEqual(self.dep().name, 'd1')

  def test_labels(self):
    self.assertEqual(self.dep().labels, {'app': 'd1', 'l1': 'v1'})

  def test_commit(self):
    kat_dep = KatDep.find('d1', self.n1)
    self.assertDictEqual(kat_dep.commit, dict(
      sha='sha',
      message='message',
      branch='branch',
      timestamp='timestamp'
    ))

  def test_image_name(self):
    self.assertEqual(self.dep().image_name, 'nginx')

  def test_container_name(self):
    self.assertEqual(self.dep().container_name, 'primary')


def create_dep(ns):
  return test_helper.create_dep(
    ns,
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
