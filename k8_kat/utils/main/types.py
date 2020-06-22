from typing import List
from typing_extensions import TypedDict


class UsageDict(TypedDict):
  cpu: str
  memory: str


class ContainerMetricsDict(TypedDict):
  usage: UsageDict


class PodMetricsDict(TypedDict):
  containers: List[ContainerMetricsDict]

