import time
from typing import List, Tuple, Dict

from kubernetes.client.rest import ApiException

from k8_kat.auth.kube_broker import broker
from k8_kat.res.events.kat_event import KatEvent
from k8_kat.utils.main import utils


class KatRes:

  def __init__(self, raw):
    self.is_dirty = False
    self.raw = raw
    self._assoced_events = None

  def __lt__(self, other):
    return self.created_at < other.created_at

  @classmethod
  def q(cls):
    delegate = cls._collection_class()
    if delegate:
      return delegate()

  @classmethod
  def is_namespaced(cls):
    return True

  @classmethod
  def find(cls, ns, name):
    try:
      return cls(cls._find(ns, name))
    except ApiException:
      return None

  @classmethod
  def _find(cls, ns, name):
    impl = cls._api_methods().get('read')
    if impl:
      if cls.is_namespaced():
        return impl(name=name, namespace=ns)
      else:
        return impl(name=name)
    else:
      raise NotImplementedError

  @classmethod
  def delete_if_exists(cls, ns, name, wait_until_gone=False):
    instance = cls.find(ns, name)
    if instance:
      instance.delete(wait_until_gone)

  def find_myself(self):
    return self._find(self.ns, self.name)

  def update(self):
    self._perform_patch_self()
    self.reload()

  def reload(self):
    try:
      self.raw = self.find_myself()
      return True
    except ApiException as e:
      return False

  @property
  def uid(self):
    return self.raw.metadata.uid

  @property
  def kind(self):
    _kind = self.raw.kind
    if not _kind:
      raise NotImplementedError
    return _kind

  @property
  def name(self):
    return self.raw.metadata.name

  @property
  def namespace(self):
    return self.raw.metadata.namespace

  @property
  def ns(self):
    return self.namespace

  @property
  def created_at(self):
    getter = lambda: self.raw.metadata.creation_timestamp
    return utils.try_or(getter)

  @property
  def labels(self):
    return self.raw.metadata.labels or {}

  @property
  def label_tups(self) -> List[Tuple[str, str]]:
    return list(self.labels.items())

  def label(self, which):
    return self.labels.get(which)

  @classmethod
  def _collection_class(cls) -> any:
    return None

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    return {}

  def wait_until(self, predicate, max_time_sec=None):
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
    if self._assoced_events is None:
      api = broker.coreV1
      raw_list = api.list_namespaced_event(namespace=self.ns).items
      kat_list = [KatEvent(raw_event) for raw_event in raw_list]
      mine = [event for event in kat_list if event.is_for(self)]
      self._assoced_events = mine
    return self._assoced_events

  def set_label(self, **labels):
    new_label_dict = {**self.labels, **labels}
    self.raw.metadata.labels = new_label_dict
    self._perform_patch_self()

  def _perform_patch_self(self):
    patch_method = self._api_methods().get('patch')
    if patch_method:
      patch_method(
        name=self.name,
        namespace=self.namespace,
        body=self.raw
      )
    else:
      raise NotImplementedError

  @classmethod
  def _api_methods(cls):
    return dict()

  def _delete(self):
    impl = self._api_methods().get('delete')
    if impl:
      if self.is_namespaced():
        impl(name=self.name, namespace=self.ns)
      else:
        impl(name=self.name)

  def delete(self, wait_until_gone=False):
    self._delete()
    if wait_until_gone:
      while self.reload():
        time.sleep(0.5)

  def serialize(self, serializer):
    return serializer(self)
