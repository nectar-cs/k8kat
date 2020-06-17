from typing import Optional

from kubernetes.client import V1ResourceQuota

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.utils.main import units
from k8_kat.utils.main.class_property import classproperty


class KatQuota(KatRes):

  @classproperty
  def kind(self):
    return "ResourceQuota"

  def body(self) -> V1ResourceQuota:
    return self.raw

  def mem_limit(self) -> Optional[float]:
    expr = self.extract_value('spec', 'hard', 'memory')
    return units.parse_quant_expr(expr)

  def mem_used(self) -> Optional[float]:
    expr = self.extract_value('status', 'used', 'memory')
    return units.parse_quant_expr(expr)

  def cpu_limit(self) -> Optional[float]:
    expr = self.extract_value('spec', 'hard', 'cpu')
    return units.parse_quant_expr(expr)

  def cpu_used(self) -> Optional[float]:
    expr = self.extract_value('status', 'used', 'cpu')
    return units.parse_quant_expr(expr)

  def extract_value(self, source_name, source_key, value_key) -> str:
    source = getattr(self.body(), source_name, None)
    values = getattr(source, source_key, {}) if source else {}
    return values.get(value_key, '') if values else ''

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_resource_quota,
      patch=broker.coreV1.patch_namespaced_resource_quota,
      delete=broker.coreV1.delete_namespaced_resource_quota,
      list=broker.coreV1.list_namespaced_resource_quota
    )
