from typing import Optional, Dict

import yaml
from kubernetes.client import V1ConfigMap

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
import json

class KatMap(KatRes):

  @property
  def kind(self):
    return "ConfigMap"

  def body(self) -> V1ConfigMap:
    return self.raw

  @property
  def data(self):
    return self.raw.data

  def jget(self, key=None) -> Optional[Dict[str, any]]:
    key = key or 'master'
    raw_value = self.data.get(key)
    return raw_value and json.loads(raw_value)

  def yget(self, key=None) -> Optional[Dict[str, any]]:
    key = key or 'master'
    raw_value = self.data.get(key)
    return raw_value and yaml.load(raw_value, Loader=yaml.FullLoader)

  def jpatch(self, content: Dict, key: str=None, merge: bool=False):
    key = key or 'master'
    content = {**self.jget(key), **content} if merge else content
    self.raw.data = ({key: json.dumps(content)})
    return self.patch()

  @classmethod
  def _api_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_config_map,
      patch=broker.coreV1.patch_namespaced_config_map,
      delete=broker.coreV1.delete_namespaced_config_map
    )
