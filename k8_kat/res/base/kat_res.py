import time
from datetime import datetime
from typing import Dict, Callable, Optional, Type, TypeVar, List

import kubernetes
from kubernetes.client.rest import ApiException

from k8_kat.auth.kube_broker import broker
from k8_kat.res.events.kat_event import KatEvent
from k8_kat.utils.main import utils, res_utils, units
from k8_kat.utils.main.class_property import classproperty


MetricsDict = TypeVar('MetricsDict')
KR = TypeVar('KR')

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
  def kind(self):
    raise NotImplementedError

  @property
  def name(self) -> str:
    return self.raw.metadata.name

  @property
  def namespace(self) -> str:
    return self.raw.metadata.namespace

  @property
  def ns(self) -> str:
    return self.namespace

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

  def cpu_usage(self) -> float:
    """Returns resource's total CPU usage in cores
    If not available pods are assigned a usage of 0."""
    return self.fetch_usage('cpu')

  def cpu_limits(self) -> Optional[float]:
    """Returns resource's total CPU limits in cores.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self.aggregate_usage(KatPod.cpu_limits)

  def cpu_requests(self) -> Optional[float]:
    """Returns resource's total CPU requests in cores.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self.aggregate_usage(KatPod.cpu_requests)

  def memory_usage(self) -> float:
    """Returns resource's total memory usage in bytes.
    If not available pods are assigned a usage of 0."""
    return self.fetch_usage('memory')

  def memory_limits(self) -> Optional[float]:
    """Returns resource's total memory limits in bytes.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self.aggregate_usage(KatPod.memory_limits)

  def memory_requests(self) -> Optional[float]:
    """Returns resource's total memory requests in bytes.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self.aggregate_usage(KatPod.memory_requests)

  def ephemeral_storage_limits(self) -> Optional[float]:
    """Returns resource's total ephemeral storage limits in bytes.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self.aggregate_usage(KatPod.ephemeral_storage_limits)

  def ephemeral_storage_requests(self) -> Optional[float]:
    """Returns resource's total ephemeral storage requests in bytes.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self.aggregate_usage(KatPod.ephemeral_storage_requests)

  def load_metrics(self) -> List[MetricsDict]:
    """Loads the appropriate metrics dict from k8s metrics API."""
    raise NotImplementedError

  def aggregate_usage(self, fn: Callable) -> Optional[float]:
    """Aggregates usage from individual pods. All most must return non-None."""
    try:
      return round(sum([fn(pod) for pod in self.pods()]), 3)
    except TypeError:
      return None

  def fetch_usage(self, resource_type: str) -> Optional[float]:
    """Fetches resources's total usage for either CPU (cores) or memory (bytes).
    """
    raw_metrics_dict: List[MetricsDict] = self.load_metrics()
    if raw_metrics_dict is None:
      return None
    total = 0
    for i in raw_metrics_dict:
      containers = i['containers']
      for c in containers:
        total += units.parse_quant_expr(utils.deep_get(c, 'usage', resource_type)) or 0
    return round(total, 3)

  def pods(self, **query) -> List[KR]:
    """Selects and returns pods associated with the object."""
    raise NotImplementedError

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
    from k8_kat.res.relation.relation import Relation
    return Relation[cls](
      model_class=cls,
      ns=ns,
      **query
    )

  @classmethod
  def wait_until_exists(cls, name: str, ns: str=None):
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

  @classmethod
  def find_res_class(cls, kind) -> Optional[Type[KR]]:
    subclasses = res_utils.kat_classes()
    matches = [sc for sc in subclasses if sc.kind == kind]
    return matches[0] if len(matches) == 1 else None


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

  def _enter_patch_loop(self, modification):
    failed_attempts = 0
    while True:
      try:
        modification(self.raw)
        self._perform_patch_self()
        return
      except kubernetes.client.rest.ApiException as e:
        if failed_attempts >= 5:
          raise e
        else:
          failed_attempts += 1
          print(f"Fail {failed_attempts} for {self.__class__.__name__}")
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



def from_dict(dict_repr: Dict):
  api = broker.client.api_client
  mocked_kube_http_resp = FakeKubeResponse(dict_repr)
  kind = dict_repr['kind']
  return api.deserialize(mocked_kube_http_resp, f"V1{kind}")


class FakeKubeResponse:
  def __init__(self, obj):
    import json
    self.data = json.dumps(obj)
