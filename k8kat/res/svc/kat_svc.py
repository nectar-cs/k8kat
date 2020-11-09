import traceback
from typing import Dict, Optional

from kubernetes.client import V1ServicePort, V1Service
from kubernetes.client.rest import ApiException

from k8kat.auth.kube_broker import broker
from k8kat.res.base import rest_backend
from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main import utils
from k8kat.utils.main.class_property import classproperty


class KatSvc(KatRes):

  @classproperty
  def kind(self):
    return "Service"

  def body(self) -> V1Service:
    return self.raw

  def proxy_get(self, path: str, args: Dict, port=None) -> Optional[str]:
    port = port if port else self.first_tcp_port_num()
    if port:
      try:
        return rest_backend.svc_proxy_get(
          name=f"{self.name}:{port}",
          namespace=self.ns,
          path=path,
          args=(args or {})
        )
      except ApiException:
        print(f"[k8kat:svc] proxy {self.name} -> {path}[{port} failed]")
        print(traceback.format_exc())
      return None
    else:
      print(f"[k8kat:svc] can't infer {self.name} port for proxy")
      return None

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    return self.raw.spec.selector or {}

  def first_tcp_port_num(self) -> Optional[int]:
    tcp_finder = lambda p: (p.protocol or '').lower() == 'tcp'
    port_obj = next(filter(tcp_finder, self.body().spec.ports), None)
    return port_obj.port if port_obj else None


  @property
  def main_port_obj(self) -> V1ServicePort:
    ports = self.raw.spec.ports
    return len(ports) and ports[0]

  @property
  def internal_ip(self) -> str:
    return self.raw.spec.cluster_ip

  @property
  def external_ip(self) -> str:
    load_bal = self.raw.status.load_balancer
    return utils.try_or(lambda: load_bal.ingress[0].ip)

  @property
  def from_port(self) -> int:
    port_obj = self.main_port_obj
    return port_obj and port_obj.port

  @property
  def to_port(self):
    port_obj = self.main_port_obj
    return port_obj and port_obj.target_port

  @property
  def short_dns(self) -> str:
    return f"{self.name}.{self.namespace}"

  @property
  def fqdn(self) -> str:
    return f"{self.short_dns}.svc.cluster.local"

  @property
  def type(self) -> str:
    return self.raw.spec.type

  def raw_endpoints(self):
    return broker.coreV1.read_namespaced_endpoints(self.name, self.ns)

  def flat_endpoints(self):
    raw_endpoints = self.raw_endpoints()
    per_sub = lambda sub: [addr for addr in (sub.addresses or [])]
    return utils.flatten([per_sub(sub) for sub in raw_endpoints.subsets])

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_service,
      patch=broker.coreV1.patch_namespaced_service,
      delete=broker.coreV1.delete_namespaced_service,
      list=broker.coreV1.list_namespaced_service
    )

  @property
  def endpoint_ips(self):
    return [ep.ip for ep in self.flat_endpoints()]
