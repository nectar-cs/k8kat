from typing import TypedDict, List


class UsageDict(TypedDict):
  cpu: str
  memory: str


class ContainerMetricsDict(TypedDict):
  usage: UsageDict


class PodMetricsDict(TypedDict):
  containers: List[ContainerMetricsDict]

