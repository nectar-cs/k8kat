import time
from datetime import datetime
from typing import Dict, Callable, Optional, Type

from kubernetes.client.rest import ApiException

from k8_kat.auth.kube_broker import broker
from k8_kat.res.events.kat_event import KatEvent
from k8_kat.utils.main import utils
from k8_kat.utils.main.class_property import classproperty


class KatRes:

  def __init__(self, raw):
    self.is_dirty = False
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

# --
# --
# --
# -------------------------------ACTION-------------------------------
# --
# --
# --

  def reload(self) -> Optional['KatRes']:
    self.raw = self.find_raw(self.name, self.ns)
    return self if self.raw else None

  @classmethod
  def list(cls, ns=None, **query):
    from k8_kat.res.relation.relation import Relation
    return Relation[cls](
      model_class=cls,
      ns=ns,
      **query
    )

  def delete(self, wait_until_gone=False):
    self._perform_delete_self()
    if wait_until_gone:
      while self.reload():
        time.sleep(0.5)

  def patch(self) -> Optional['KatRes']:
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
    combined_annotations = {**self.annotations, **annotations}
    self.raw.metadata.annotations = combined_annotations
    if save:
      self.patch()

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
  def inflate(cls, raw) -> 'KatRes':
    host = cls.find_res_class(raw.kind)
    return host(raw) if host else None

  @classmethod
  def find_res_class(cls, kind) -> Optional[Type['KatRes']]:
    subclasses = KatRes.__subclasses__()
    # noinspection PyUnresolvedReferences
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
