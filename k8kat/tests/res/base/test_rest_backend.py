from kubernetes.client import V1ConfigMap, V1ObjectMeta

from k8kat.auth.kube_broker import broker
from k8kat.res.base import rest_backend
from k8kat.res.base.kat_res import auto_namespaced_kat_cls
from k8kat.res.config_map.kat_map import KatMap
from k8kat.tests.res.base.cluster_test import ClusterTest
from k8kat.utils.testing import ns_factory


class TestRestBackend(ClusterTest):

  def test_delete_namespaced_resource(self):
    ns, = ns_factory.request(1)
    broker.coreV1.create_namespaced_config_map(ns, body=V1ConfigMap(
      metadata=V1ObjectMeta(name='victim'),
      data={}
    ))

    self.assertIsNotNone(KatMap.find('victim', ns))
    rest_backend.delete_namespaced_resource(
      'configmaps',
      '',
      ns,
      'victim'
    )
    self.assertIsNone(KatMap.find('victim', ns))

  def test_list_namespaced(self):
    ns, = ns_factory.request(1)
    rest_backend.list_namespaced_resources(
      'deployments',
      'apps/v1',
      'default'
    )
    rest_backend.list_namespaced_resources(
      'deployments',
      'apps',
      'default'
    )
    rest_backend.list_namespaced_resources(
      'persistentvolumeclaims',
      '',
      'default'
    )

  def test_auto_namespaced_kat_cls(self):
    auto_cls = auto_namespaced_kat_cls('deployments')
    auto_cls.list('default')
    auto_cls = auto_namespaced_kat_cls('roles')
    auto_cls.list('default')
    auto_cls = auto_namespaced_kat_cls('pods')
    auto_cls.list('default')
    auto_cls = auto_namespaced_kat_cls('jobs')
    auto_cls.list('default')
    self.assertIsNone(auto_namespaced_kat_cls('not-real'))

  def test_auto_namespaced_kat_cls2(self):
    auto_cls = auto_namespaced_kat_cls('replicasets')
    self.assertEqual('ReplicaSet', auto_cls.kind)
    self.assertEqual('replicasets', auto_cls.res_name_plural)

    auto_cls = auto_namespaced_kat_cls('rolebinding')
    self.assertEqual('RoleBinding', auto_cls.kind)
    self.assertEqual('rolebindings', auto_cls.res_name_plural)

  def test_request_sig(self):
    self.assertEqual('/api/v1', rest_backend.request_sig(''))
    self.assertEqual('/api/v1', rest_backend.request_sig('v1'))
    self.assertEqual('/apis/foo/v1', rest_backend.request_sig('foo'))
    self.assertEqual('/apis/foo/v2', rest_backend.request_sig('foo/v2'))
    self.assertEqual('/apis/foo.bar/v1', rest_backend.request_sig('foo.bar'))
