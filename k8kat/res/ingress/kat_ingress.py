from typing import List, Dict

from kubernetes.client import ExtensionsV1beta1Ingress, ExtensionsV1beta1IngressRule, ExtensionsV1beta1HTTPIngressPath

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main.class_property import classproperty


class KatIngress(KatRes):

  @classproperty
  def kind(self):
    return 'Ingress'

  def body(self) -> ExtensionsV1beta1Ingress:
    return self.raw

  def basic_rules(self) -> Dict[str, List[Dict[str, str]]]:
    result = {}
    rules: List[ExtensionsV1beta1IngressRule] = self.body().spec.rules
    for rule in rules:
      if rule.host:
        bundles = []
        ingress_paths: List[ExtensionsV1beta1HTTPIngressPath] = rule.http.paths
        for ingress_path in ingress_paths:
          bundles.append(dict(
            service=ingress_path.backend.service_name,
            port=ingress_path.backend.service_port,
            path=ingress_path.path
          ))
        result[rule.host] = bundles
    return result


  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.extsV1.read_namespaced_ingress,
      patch=broker.extsV1.patch_namespaced_ingress,
      delete=broker.extsV1.delete_namespaced_ingress,
      list=broker.extsV1.list_namespaced_ingress
    )
