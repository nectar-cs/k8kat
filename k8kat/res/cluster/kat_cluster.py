from typing import List

from k8kat.auth.kube_broker import broker
from k8kat.res.node.kat_node import KatNode
from k8kat.utils.main import utils, units
from k8kat.utils.main.types import NodeMetricsDict


class KatCluster:

  @classmethod
  def load_per_node_metrics(cls) -> List[NodeMetricsDict]:
    return broker.custom.list_cluster_custom_object(
      group='metrics.k8s.io',
      version='v1beta1',
      plural='nodes'
    ).get('items', [])

  @classmethod
  def resources_available(cls):
    nodes = KatNode.list()
    per_node_cpu = [n.cpu_capacity() or 0 for n in nodes]
    per_node_mem = [n.mem_capacity() or 0 for n in nodes]
    return sum(per_node_cpu), sum(per_node_mem)

  @classmethod
  def resources_used(cls):
    per_node_metrics = cls.load_per_node_metrics()
    per_node_cpu = [read_node_res_used(m, 'cpu') for m in per_node_metrics]
    per_node_mem = [read_node_res_used(m, 'memory') for m in per_node_metrics]
    return sum(per_node_cpu), sum(per_node_mem)

def read_node_res_used(node_metrics: NodeMetricsDict, resource_type: str):
  metric_deep_key = ('usage', resource_type)
  usage_quant_expr = utils.deep_get(node_metrics, *metric_deep_key)
  quant_bytes = units.parse_quant_expr(usage_quant_expr or '0')
  return quant_bytes or 0
