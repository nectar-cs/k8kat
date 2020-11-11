import time
from datetime import datetime
from typing import Dict, Callable, Optional, Type, TypeVar, List

import kubernetes
from cachetools.func import lru_cache
from kubernetes.client import ApiClient
from kubernetes.client.rest import ApiException

from k8kat.auth.kube_broker import broker
from k8kat.res.base import rest_backend
from k8kat.res.events.kat_event import KatEvent
from k8kat.utils.main import utils, res_utils, units
from k8kat.utils.main.api_defs_man import api_defs_man
from k8kat.utils.main.class_property import classproperty
from k8kat.utils.main.types import PodMetricsDict

MetricsDict = TypeVar('MetricsDict')
KR = TypeVar('KR', bound='KatRes')


class KatRes:

  def __init__(self, raw):
    self.is_dirty = False
    if type(raw) == dict:
      raw = from_dict(raw)
    self.raw = raw

# --
# --
# --
# -------------------------------PROPERTIES-------------------------------
# --
# --
# --

  @property
  def uid(self):
    return self.raw.metadata.uid

  @classproperty
  def kind(self) -> str:
    raise NotImplementedError

  @classproperty
  def res_name_plural(self):
    return f"{self.kind.lower()}s"

  @classproperty
  def kind_aliases(self) -> List[str]:
    return [
      self.kind,
      self.kind.lower(),
      self.res_name_plural
    ]

  @property
  def name(self) -> str:
    return self.raw.metadata.name

  @property
  def namespace(self) -> str:
    return self.raw.metadata.namespace

  def sig(self, with_ns=False):
    ns_less = f'{self.kind}:{self.name}'
    return f'{self.ns}:{ns_less}' if with_ns else ns_less

  @property
  def ns(self) -> str:
    return self.namespace

  @property
  def metrics_component(self):
    return None

  @property
  def labels(self) -> Dict[str, str]:
    return self.raw.metadata.labels or {}

  @property
  def annotations(self) -> Dict[str, str]:
    return self.raw.metadata.annotations or {}

  @property
  def created_at(self) -> Optional[str]:
    ts = self.raw.metadata.creation_timestamp
    return ts.isoformat(' ', 'seconds') if ts else None

# --
# --
# --
# -------------------------------INTEL-------------------------------
# --
# --
# --

  def ternary_status(self):
    return 'positive'

  def __lt__(self, other):
    return self.created_at < other.created_at

  def has_settled(self):
    return True

  def updated_at(self) -> str:
    return self.annotations.get('updated_at') or \
           self.created_at

  def short_desc(self):
    return self.annotations.get('short_desc')

# --
# --
# --
# -------------------------------ACTION-------------------------------
# --
# --
# --

  def reload(self) -> Optional[KR]:
    self.raw = self.find_raw(self.name, self.ns)
    return self if self.raw else None

  @classmethod
  def list(cls, ns=None, **query) -> List[KR]:
    from k8kat.res.relation.relation import Relation
    return Relation[cls](
      model_class=cls,
      ns=ns,
      **query
    )

  @classmethod
  def list_excluding_sys(cls, ns=None, **query) -> List[KR]:
    return cls.list(ns, **query)

  @classmethod
  def wait_until_exists(cls, name: str, ns: str = None):
    res = None
    for attempts in range(0, 20):
      res = cls.find(name, ns)
      if res:
        break
      else:
        time.sleep(1)
    return res

  def delete(self, wait_until_gone=False):
    self._perform_delete_self()
    if wait_until_gone:
      while self.reload():
        time.sleep(0.5)

  def patch(self, modifier=None) -> Optional[KR]:
    if modifier is not None:
      self._enter_patch_loop(modifier)
    else:
      self._perform_patch_self()
    return self.reload()

  def wait_until(self, predicate, max_time_sec=None) -> bool:
    start_time = time.time()
    condition_met = False
    for attempts in range(0, 50):
      if predicate():
        condition_met = True
        break
      else:
        if max_time_sec and time.time() - start_time > max_time_sec:
          return False
        time.sleep(1)
        self.reload()
    return condition_met

  def events(self):
    api = broker.coreV1
    raw_list = api.list_namespaced_event(namespace=self.ns).items
    kat_list = [KatEvent(raw_event) for raw_event in raw_list]
    return [event for event in kat_list if event.is_for(self)]

  def trigger(self):
    self.annotate(trigger=utils.rand_str())

  def touch(self, save=True):
    self.annotate(save=save, updated_at=str(datetime.now()))

  def annotate(self, save=True, **annotations):
    def perf(raw):
      existing = raw.metadata.annotations or {}
      combined = {**existing, **annotations}
      raw.metadata.annotations = combined

    self.patch(perf) if save else perf(self.raw)

  def label(self, save=True, **labels):
    def perf(raw):
      existing = raw.metadata.labels or {}
      combined = {**existing, **labels}
      raw.metadata.labels = combined

    self.patch(perf) if save else perf(self.raw)

# --
# --
# --
# -------------------------------CLASS-------------------------------
# --
# --
# --

  @classmethod
  def find_raw(cls, name, ns=None):
    try:
      fn: Callable = cls.k8s_verb_methods().get('read')
      is_ns: bool = cls.is_namespaced()
      return fn(name=name, namespace=ns) if is_ns else fn(name=name)
    except ApiException:
      return None

  @classmethod
  def find(cls, name, ns=None):
    raw_res = cls.find_raw(name, ns)
    return cls(raw_res) if raw_res else None

  @classmethod
  def delete_if_exists(cls, ns, name, wait_until_gone=False):
    instance = cls.find(name, ns)
    if instance:
      instance.delete(wait_until_gone)

  @classmethod
  def k8s_verb_methods(cls) -> Dict[str, Callable]:
    return dict()

  @classmethod
  def is_namespaced(cls) -> bool:
    return True

  @classmethod
  def inflate(cls, raw) -> KR:
    host = cls.find_res_class(raw.kind)
    return host(raw) if host else None

  @staticmethod
  def find_res_class(kind: str) -> Optional[Type[KR]]:
    subclasses = res_utils.kat_classes()
    predicate = lambda s: kind in s.kind_aliases
    return next(filter(predicate, subclasses), None)

  @classmethod
  def class_for(cls, kind: str) -> Optional[Type[KR]]:
    expl_class = cls.find_res_class(kind)
    return expl_class or auto_namespaced_kat_cls(kind)

# --
# --
# --
# -------------------------------USAGE / REQ / LIM-------------------------------
# --
# --
# --

  def load_per_pod_metrics(self) -> Optional[List[PodMetricsDict]]:
    """Loads the appropriate metrics dict from k8s metrics API."""
    return None

  def cpu_used(self) -> float:
    """Returns resource's total CPU usage in cores or 0"""
    return self._resource_usage('cpu') or 0

  def mem_used(self) -> float:
    """Returns resource's total memory usage in bytes or 0"""
    return self._resource_usage('memory') or 0

  def _resource_usage(self, resource_type: str) -> Optional[float]:
    per_pod_metrics: List[PodMetricsDict] = self.load_per_pod_metrics()
    if per_pod_metrics is not None:
      total = 0
      for pod_metrics in per_pod_metrics:
        per_container_metrics = pod_metrics.get('containers', [])
        for container_metrics in per_container_metrics:
          container_metrics = container_metrics or {}
          metric_deep_key = ('usage', resource_type)
          usage_quant_expr = utils.deep_get(container_metrics, *metric_deep_key)
          usage_quant = units.parse_quant_expr(usage_quant_expr)
          total += usage_quant or 0
      return round(total, 3)
    else:
      return None

  @lru_cache(maxsize=128)
  def pods(self):
    return []

  def _sum_pod_req_or_lim(self, func):
    bytes_per_pod = [func(pod) for pod in self.pods()]
    bytes_per_pod = [value or 0 for value in bytes_per_pod]
    return sum(bytes_per_pod)

  def pods_cpu_limit(self) -> Optional[float]:
    return self._sum_pod_req_or_lim(lambda p: p.cpu_limit())

  def pods_cpu_request(self) -> Optional[float]:
    return self._sum_pod_req_or_lim(lambda p: p.cpu_request())

  def pods_mem_limit(self) -> Optional[float]:
    return self._sum_pod_req_or_lim(lambda p: p.mem_limit())

  def pods_mem_request(self) -> Optional[float]:
    return self._sum_pod_req_or_lim(lambda p: p.mem_request())

# --
# --
# --
# -------------------------------PLUMBING-------------------------------
# --
# --
# --

  def _perform_patch_self(self):
    patch_method = self.k8s_verb_methods().get('patch')
    self.ns_agnostic_call(patch_method, body=self.raw)

  def _enter_patch_loop(self, modification_delegate: Callable):
    failed_attempts = 0
    while True:
      try:
        modification_delegate(self.raw)
        self._perform_patch_self()
        return
      except kubernetes.client.rest.ApiException as e:
        if failed_attempts >= 5:
          raise e
        else:
          failed_attempts += 1
          time.sleep(1)
          self.reload()

  def _perform_delete_self(self):
    impl = self.k8s_verb_methods().get('delete')
    self.ns_agnostic_call(impl)

  def ns_agnostic_call(self, impl: Callable, **kwargs) -> any:
    if self.is_namespaced():
      return impl(name=self.name, namespace=self.ns, **kwargs)
    else:
      return impl(name=self.name, **kwargs)

  def serialize(self, serializer):
    return serializer(self)


def auto_namespaced_kat_cls(res_name_or_kind: str) -> Optional[Type[KatRes]]:
  definition = api_defs_man.find_def(res_name_or_kind)
  if definition:
    class NsdKatShell(KatRes):
      @classproperty
      def kind(self) -> str:
        return definition['kind']

      @classproperty
      def res_name_plural(self) -> str:
        return definition['name']

      @classmethod
      def is_namespaced(cls) -> bool:
        return True

      @classmethod
      def k8s_verb_methods(cls) -> Dict[str, Callable]:
        def _list(namespace, **kwargs):
          return rest_backend.list_namespaced_resources(
            definition['name'],
            definition['apigroup'],
            namespace,
            **kwargs
          )

        def _delete(name, namespace, **kwargs):
          return rest_backend.delete_namespaced_resource(
            definition['name'],
            definition['apigroup'],
            namespace,
            name,
            **kwargs
          )

        return dict(
          list=_list,
          delete=_delete
        )
    return NsdKatShell
  else:
    return None


def from_dict(dict_repr: Dict):
  api = ApiClient()
  mocked_kube_http_resp = FakeKubeResponse(dict_repr)
  kind = dict_repr['kind']
  return api.deserialize(mocked_kube_http_resp, f"V1{kind}")


class FakeKubeResponse:
  def __init__(self, obj):
    import json
    self.data = json.dumps(obj)
