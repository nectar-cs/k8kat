from k8kat.res.base import rest_backend
from k8kat.res.base.kat_res import auto_namespaced_kat_cls
from k8kat.tests.res.base.cluster_test import ClusterTest
from k8kat.utils.testing import ns_factory


class TestRestBackend(ClusterTest):

  def test_list_namespaced(self):
    ns, = ns_factory.request(1)
    result = rest_backend.list_namespaced(
      'deployments',
      'apps/v1',
      'default'
    )

    result = rest_backend.list_namespaced(
      'persistentvolumeclaims',
      '',
      'default'
    )
    print(result)

  def test_auto_namespaced_kat_cls(self):
    auto_cls = auto_namespaced_kat_cls(
      'deployments',
      'apps/v1',
    )
    auto_cls.list('default')
