from typing import Callable

from k8_kat.res.nodes.kat_node import KatNode


def aggregate_usage(fn: Callable) -> float:
  return sum([(fn(node) or 0) for node in KatNode.list()])


class KatCluster:

  @classmethod
  def cpu_capacity(cls) -> float:
    return aggregate_usage(KatNode.cpu_capacity)

  @classmethod
  def mem_capacity(cls) -> float:
    return aggregate_usage(KatNode.mem_capacity)
