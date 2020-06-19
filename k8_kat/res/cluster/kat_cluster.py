from typing import Callable, Optional

from k8_kat.res.nodes.kat_node import KatNode


def aggregate_usage(fn: Callable) -> float:
  return sum([(fn(node) or 0) for node in KatNode.list()])


class KatCluster:

  @classmethod
  def cpu_capacity(cls) -> float:
    """Aggregates and returns CPU capacity from nodes in cluster."""
    return aggregate_usage(KatNode.cpu_capacity)

  @classmethod
  def cpu_usage(cls) -> float:
    """Aggregates and returns CPU usage from nodes in cluster (in cores)."""
    return aggregate_usage(KatNode.cpu_usage)

  @classmethod
  def cpu_limits(cls) -> Optional[float]:
    """Aggregates and returns CPU limits from nodes in cluster (in cores)."""
    return aggregate_usage(KatNode.cpu_limits)

  @classmethod
  def cpu_requests(cls) -> Optional[float]:
    """Aggregates and returns CPU requests from nodes in cluster (in cores)."""
    return aggregate_usage(KatNode.cpu_requests)

  @classmethod
  def mem_capacity(cls) -> float:
    """Aggregates and returns memory capacity from nodes in cluster."""
    return aggregate_usage(KatNode.mem_capacity)

  @classmethod
  def memory_usage(cls) -> float:
    """Aggregates and returns memory usage from nodes in cluster (in bytes)."""
    return aggregate_usage(KatNode.memory_usage)

  @classmethod
  def memory_limits(cls) -> Optional[float]:
    """Aggregates and returns memory limits from nodes in cluster (in bytes)."""
    return aggregate_usage(KatNode.memory_limits)

  @classmethod
  def memory_requests(cls) -> Optional[float]:
    """Aggregates and returns memory requests from nodes in cluster (in bytes)."""
    return aggregate_usage(KatNode.memory_requests)