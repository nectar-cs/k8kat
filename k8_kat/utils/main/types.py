from typing import List, Optional
from typing_extensions import TypedDict


class UsageDict(TypedDict):
  cpu: Optional[str]
  memory: Optional[str]


class ContainerMetricsDict(TypedDict):
  usage: UsageDict


class PodMetricsDict(TypedDict):
  containers: List[ContainerMetricsDict]


class NodeMetricsDict(TypedDict):
  usage: UsageDict

