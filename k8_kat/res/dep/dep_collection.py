from k8_kat.res.base.res_collection import ResCollection
from k8_kat.res.base.res_query import ResQuery
from k8_kat.res.dep.dep_query_exec import DepQueryExec
from k8_kat.res.dep.kat_dep import KatDep


class DepCollection(ResCollection):
  def create_query(self):
    return ResQuery(DepQueryExec(), KatDep)
