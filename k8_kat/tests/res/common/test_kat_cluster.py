from unittest.mock import patch

from k8_kat.res.cluster.kat_cluster import KatCluster
from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.main.types import NodeMetricsDict, UsageDict


class TestKatConfigMap(ClusterTest):

  def test_resources_used(self):
    with patch.object(KatCluster, 'load_per_node_metrics') as mock_metrics:
      mock_metrics.return_value = [
        NodeMetricsDict(usage={}),
        NodeMetricsDict(usage=UsageDict(cpu=None, memory=None)),
        NodeMetricsDict(usage=UsageDict(cpu=None, memory='10M')),
        NodeMetricsDict(usage=UsageDict(cpu='.25', memory=None)),
        NodeMetricsDict(usage=UsageDict(cpu='750m', memory='90e6'))
      ]
      cpu_used, mem_used = KatCluster.resources_used()
      self.assertEqual(cpu_used, 1)
      self.assertEqual(mem_used, 100_000_000)
