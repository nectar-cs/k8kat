from typing import Optional, List, TypedDict

from k8_kat.utils.main import utils, units
from k8_kat.utils.main.types import PodMetricsDict, ContainerMetricsDict


class WorkloadHost:

  def cpu_used(self) -> float:
    """Returns resource's total CPU usage in cores
    If not available pods are assigned a usage of 0."""
    return self.resource_usage('cpu')

  def memory_used(self) -> float:
    """Returns resource's total memory usage in bytes.
    If not available pods are assigned a usage of 0."""
    return self.resource_usage('memory')

  def load_metrics(self) -> List[PodMetricsDict]:
    """Loads the appropriate metrics dict from k8s metrics API."""
    raise NotImplementedError

  def resource_usage(self, resource_type: str) -> Optional[float]:
    """Fetches resources's total usage for either CPU (cores) or memory (bytes).
    """
    per_pod_metrics: List[PodMetricsDict] = self.load_metrics() or []
    total = 0

    for i in per_pod_metrics:
      per_container_metrics: List[ContainerMetricsDict] = i['containers']
      for container_metrics in per_container_metrics:
        usage_quant_expr = utils.deep_get(container_metrics, 'usage', resource_type)
        usage_quant = units.parse_quant_expr(usage_quant_expr)
        total += usage_quant or 0
    return round(total, 3)

  def pods(self, **query):
    """Selects and returns pods associated with the object."""
    raise NotImplementedError

