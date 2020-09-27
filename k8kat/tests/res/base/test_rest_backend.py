from k8kat.res.base import rest_backend
from k8kat.res.base.kat_res import auto_namespaced_kat_cls
from k8kat.tests.res.base.cluster_test import ClusterTest
from k8kat.utils.testing import ns_factory


class TestRestBackend(ClusterTest):

  def test_list_namespaced(self):
    ns, = ns_factory.request(1)
    rest_backend.list_namespaced(
      'deployments',
      'apps/v1',
      'default'
    )
    rest_backend.list_namespaced(
      'deployments',
      'apps',
      'default'
    )
    rest_backend.list_namespaced(
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



def test_request_sig(self):
    self.assertEqual('/api/v1', rest_backend.request_sig(''))
    self.assertEqual('/api/v1', rest_backend.request_sig('v1'))
    self.assertEqual('/apis/foo/v1', rest_backend.request_sig('foo'))
    self.assertEqual('/apis/foo/v2', rest_backend.request_sig('foo/v2'))
    self.assertEqual('/apis/foo.bar/v1', rest_backend.request_sig('foo.bar'))
