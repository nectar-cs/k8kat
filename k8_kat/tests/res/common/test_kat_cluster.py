from k8_kat.res.cluster.kat_cluster import KatCluster
from k8_kat.tests.res.base.cluster_test import ClusterTest


class TestKatConfigMap(ClusterTest):

  def test_cpu_used(self):
    metrics = KatCluster.load_metrics()
    print(metrics)

