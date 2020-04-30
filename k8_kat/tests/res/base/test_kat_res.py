from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.testing import ns_factory


class Base:
  class TestKatRes(ClusterTest):

    def setUp(self) -> None:
      self.parent_ns, = ns_factory.request(1)

    def tearDown(self) -> None:
      ns_factory.relinquish(self.parent_ns)

    def test_find(self):
      self.create_res(self.parent_ns, 'foo')
      found = self.res_class().find(self.parent_ns, 'foo')
      self.assertIsNotNone(found)
      self.assertEqual(found.metadata.name, 'foo')

    # def test_reload(self):
    #   pass
    #
    # def test_update(self):
    #   pass
    #
    # def test_delete(self):
    #   pass

    def create_res(self, ns, name):
      raise NotImplementedError

    def res_class(self):
      raise NotImplementedError
