from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.testing import ns_factory


class Base:
  class TestKatRes(ClusterTest):

    def setUp(self) -> None:
      self.pns, = ns_factory.request(1)

    def tearDown(self) -> None:
      ns_factory.relinquish(self.pns)

    def test_find_namespaced(self):
      print(f"Got my ns {self.pns}")
      self.create_res('foo', self.pns)
      found = self.res_class().find('foo', self.pns)
      self.assertIsNotNone(found)
      self.assertEqual(found.raw.metadata.name, 'foo')

    # def test_reload(self):
    #   pass
    #
    # def test_update(self):
    #   pass
    #
    # def test_delete(self):
    #   pass

    def create_res(self, name, ns=None):
      raise NotImplementedError

    def res_class(self):
      raise NotImplementedError
