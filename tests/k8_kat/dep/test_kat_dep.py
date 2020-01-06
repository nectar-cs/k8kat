import unittest

from k8_kat.dep.kat_dep import KatDep
from tests.k8_kat.base.k8_kat_test import ClusterTest


class TestKatDep(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatDep, cls).setUpClass()
    cls.create_dep('n1', 'd1')
    cls.nk_label_dep('n1', 'd1', [('l1', 'v1')])

  def test_name(self):
    kat_dep = KatDep(self.read_dep('n1', 'd1'))
    self.assertEqual(kat_dep.name, 'd1')

  def test_labels(self):
    kat_dep = KatDep(self.read_dep('n1', 'd1'))
    self.assertEqual(kat_dep.labels, {'app': 'd1', 'l1': 'v1'})

  def test_commit(self):
    self.nk_apply('n1', 'commit-annotated-dep')
    kat_dep = KatDep(self.read_dep('n1', 'da1'))
    self.assertDictEqual(kat_dep.commit, ({
      'sha': 'sha',
      'message': 'message',
      'branch': 'branch',
      'timestamp': 'timestamp'
    }))

    kat_dep = KatDep(self.read_dep('n1', 'd1'))
    self.assertDictEqual(kat_dep.commit, ({
      'sha': None,
      'message': None,
      'branch': None,
      'timestamp': None
    }))

  def test_image_name(self):
    kat_dep = KatDep(self.read_dep('n1', 'd1'))
    self.assertEqual(kat_dep.image_name, 'nginx')

  def test_container_name(self):
    kat_dep = KatDep(self.read_dep('n1', 'd1'))
    self.assertEqual(kat_dep.container_name, 'nginx')


if __name__ == '__main__':
    unittest.main()
