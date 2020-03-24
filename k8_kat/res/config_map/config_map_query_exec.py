from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.res_query_exec import ResQueryExec


class ConfigMapQueryExec(ResQueryExec):

  @staticmethod
  def fetch_for_single_ns(ns, label_exp):
    return broker.coreV1.list_namespaced_config_map(
      namespace=ns,
      label_selector=label_exp
    ).items

  @staticmethod
  def fetch_for_all_ns(label_exp):
    return broker.coreV1.list_config_map_for_all_namespaces(
      label_selector=label_exp
    ).items


