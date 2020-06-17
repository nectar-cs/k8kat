from k8_kat.res.nodes.kat_node import KatNode


class KatCluster:

  @classmethod
  def cpu_capacity(cls) -> float:
    return sum([n.cpu_capacity for n in KatNode.list()])

  @classmethod
  def mem_capacity(cls) -> float:
    return sum([n.mem_capacity() or 0 for n in KatNode.list()])
