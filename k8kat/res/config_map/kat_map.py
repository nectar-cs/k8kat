from typing import Optional, Dict

import yaml
from kubernetes.client import V1ConfigMap

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes
import json

from k8kat.utils.main.class_property import classproperty


class KatMap(KatRes):

  @classproperty
  def kind(self):
    return "ConfigMap"

  def body(self) -> V1ConfigMap:
    return self.raw

  @property
  def data(self):
    return self.raw.data

  def jget(self, key=None, backup=None) -> Optional[Dict[str, any]]:
    key = key or 'master'
    raw_value = self.data.get(key)
    obtained = raw_value and json.loads(raw_value)
    return obtained if obtained is not None else backup

  def yget(self, key=None, backup=None) -> Optional[Dict[str, any]]:
    key = key or 'master'
    raw_value = self.data.get(key)
    obtained = raw_value and yaml.load(raw_value, Loader=yaml.FullLoader)
    return obtained if obtained is not None else backup

  def jpatch(self, content: Dict, key: str = None, merge: bool = False):
    key = key or 'master'
    content = {**self.jget(key), **content} if merge else content
    self.raw.data = ({key: json.dumps(content)})
    return self.patch()

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_config_map,
      patch=broker.coreV1.patch_namespaced_config_map,
      delete=broker.coreV1.delete_namespaced_config_map,
      list=broker.coreV1.list_namespaced_config_map
    )
