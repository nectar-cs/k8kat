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

  def mem_request_sum_allowed(self, target_unit='') -> Optional[float]:
    expr = self.extract_value('spec', 'hard', 'memory')
    return units.parse_quant_expr(expr, target_unit)

  def mem_request_sum_deployed(self, target_unit='') -> Optional[float]:
    expr = self.extract_value('status', 'used', 'memory')
    return units.parse_quant_expr(expr, target_unit)

  def mem_limit_sum_allowed(self, target_unit='') -> Optional[float]:
    expr = self.extract_value('spec', 'hard', 'limits.memory')
    return units.parse_quant_expr(expr, target_unit)

  def mem_limit_sum_deployed(self, target_unit='') -> Optional[float]:
    expr = self.extract_value('status', 'used', 'limits.memory')
    return units.parse_quant_expr(expr, target_unit)

  def cpu_request_sum_allowed(self, target_unit='') -> Optional[float]:
    expr = self.extract_value('spec', 'hard', 'cpu')
    return units.parse_quant_expr(expr, target_unit)

  def cpu_request_sum_deployed(self, target_unit='') -> Optional[float]:
    expr = self.extract_value('status', 'used', 'cpu')
    return units.parse_quant_expr(expr, target_unit)

  def cpu_limit_sum_allowed(self, target_unit='') -> Optional[float]:
    expr = self.extract_value('spec', 'hard', 'limits.cpu')
    return units.parse_quant_expr(expr, target_unit)

  def cpu_limit_sum_deployed(self, target_unit='') -> Optional[float]:
    expr = self.extract_value('status', 'used', 'limits.cpu')
    return units.parse_quant_expr(expr, target_unit)

  def extract_value(self, source_name, source_key, value_key) -> str:
    source = getattr(self.body(), source_name, None)
    values = getattr(source, source_key, {}) if source else {}
    result = (values or {}).get(value_key, '')
    if not result and 'requests.' not in value_key:
      result = (values or {}).get(f"requests.{value_key}", '')
    return result

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_resource_quota,
      patch=broker.coreV1.patch_namespaced_resource_quota,
      delete=broker.coreV1.delete_namespaced_resource_quota,
      list=broker.coreV1.list_namespaced_resource_quota
    )
