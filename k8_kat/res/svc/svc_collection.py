from k8_kat.res.base.res_collection import ResCollection
from k8_kat.res.base.res_query import ResQuery
from k8_kat.res.svc.kat_svc import KatSvc
from k8_kat.res.svc.svc_query_exec import SvcQueryExec


class SvcCollection(ResCollection):
  def create_query(self):
    return ResQuery(SvcQueryExec(), KatSvc)

  def cluster_ip(self):
    return self.feature_is('type', 'ClusterIP')

  def node_port(self):
    return self.feature_is('type', 'NodePort')

  def pending(self):
    return self.feature_is('external_ip', None)
