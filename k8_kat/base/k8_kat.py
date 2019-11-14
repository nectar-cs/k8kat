from k8_kat.dep.dep_collection import DepCollection
from k8_kat.svc.svc_collection import SvcCollection


class K8kat:

  @staticmethod
  def deps(**kwargs) -> DepCollection:
    collection = DepCollection()
    return collection.where(**kwargs)

  @staticmethod
  def svcs(**kwargs) -> SvcCollection:
    collection = SvcCollection()
    return collection.where(**kwargs)
