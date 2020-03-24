from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
import json


class KatMap(KatRes):

  @property
  def data(self):
    return self.raw.data

  def json(self, field_name):
    raw_value = self.data.get(field_name)
    if raw_value is not None:
      try:
        return json.loads(raw_value)
      except json.decoder.JSONDecodeError:
        return None
    else:
      return None

  def set_json(self, key, dictionary):
    self.set_data({key: json.dumps(dictionary)})

  def set_data(self, new_data):
    self.raw.data = new_data
    self.update()

  def merge_data(self, **new_data):
    self.raw.data = {**self.raw.data, **new_data}
    self.update()

  @property
  def kind(self):
    return "ConfigMap"

  @classmethod
  def _find(cls, ns, name):
    return broker.coreV1.read_namespaced_config_map(
      namespace=ns,
      name=name
    )

  @classmethod
  def _collection_class(cls):
    from k8_kat.res.config_map.config_map_collection import ConfigMapCollection
    return ConfigMapCollection()

  def _perform_patch_self(self):
    broker.coreV1.patch_namespaced_config_map(
      name=self.name,
      namespace=self.namespace,
      body=self.raw
    )
