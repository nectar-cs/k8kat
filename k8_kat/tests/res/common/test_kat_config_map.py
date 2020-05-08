import json

import yaml
from kubernetes.client import V1ConfigMap, V1ObjectMeta

from k8_kat.auth.kube_broker import broker
from k8_kat.res.config_map.kat_map import KatMap
from k8_kat.tests.res.base.test_kat_res import Base


class TestKatConfigMap(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None, data=None):
    data = data if data else dict(foo='bar')
    return broker.coreV1.create_namespaced_config_map(
      namespace=ns,
      body=V1ConfigMap(
        metadata=V1ObjectMeta(name=name),
        data=data
      )
    )

  @classmethod
  def res_class(cls):
    return KatMap

  def test_jget(self):
    raw = create_jmap(self.res_name, self.pns, dict(foo='bar'))
    self.assertEqual(KatMap(raw).jget(), dict(foo='bar'))

  def test_yget(self):
    raw = create_ymap(self.res_name, self.pns, dict(foo='bar'))
    self.assertEqual(KatMap(raw).yget(), dict(foo='bar'))

  def test_jpatch_no_merge(self):
    initial_content = dict(foo='bar')
    kat_map = KatMap(create_ymap(self.res_name, self.pns, initial_content))
    kat_map.jpatch(content=dict(foo='baz', bar='baz'))
    self.assertEqual(kat_map.jget(), dict(foo='baz', bar='baz'))


def create_jmap(name, ns, contents, master_key=None) -> V1ConfigMap:
  master_key = master_key or 'master'
  return broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(name=name),
      data={master_key: json.dumps(contents)}
    )
  )

def create_ymap(name, ns, contents, master_key=None) -> V1ConfigMap:
  master_key = master_key or 'master'
  return broker.coreV1.create_namespaced_config_map(
    namespace=ns,
    body=V1ConfigMap(
      metadata=V1ObjectMeta(name=name),
      data={master_key: yaml.dump(contents)}
    )
  )
