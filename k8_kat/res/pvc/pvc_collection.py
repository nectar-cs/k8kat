from k8_kat.res.base.res_collection import ResCollection
from k8_kat.res.base.res_query import ResQuery
from k8_kat.res.config_map.config_map_query_exec import ConfigMapQueryExec
from k8_kat.res.config_map.kat_map import KatMap


class PvcCollection(ResCollection):
  def create_query(self):
    return ResQuery(ConfigMapQueryExec(), KatMap)
