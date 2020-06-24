from k8_kat.res.node.kat_node import KatNode
from k8_kat.tests.res.base.cluster_test import ClusterTest


class TestKatNode(ClusterTest):

  def test_capacity(self):
    node = KatNode.list()[0]
    self.assertGreater(node.cpu_capacity(), 1)
    self.assertGreater(node.mem_capacity(), 1)
