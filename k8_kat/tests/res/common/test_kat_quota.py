from typing import Type

from kubernetes.client import V1ResourceQuota, V1ObjectMeta, V1ResourceQuotaSpec

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.res.quotas.kat_quota import KatQuota
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils
from k8_kat.utils.testing import simple_pod, ns_factory


class TestKatQuota(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return create(name, ns)

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatQuota

  def test_requests_and_limits_allowed(self):
    args = {
      'requests.cpu': '1.1',
      'memory': '10M',
      'limits.memory': '20M'
    }

    quota = KatQuota(create(self.res_name, self.pns, **args))
    self.assertEqual(1.1, quota.cpu_request_sum_allowed())
    self.assertEqual(10_000_000, quota.mem_request_sum_allowed())

    self.assertEqual(None, quota.cpu_limit_sum_allowed())
    self.assertEqual(20_000_000, quota.mem_limit_sum_allowed())

  def test_requests_and_limits_deployed(self):
    ns, = ns_factory.request(1)
    pod = KatPod(simple_pod.create(
      ns=ns,
      name=utils.rand_str(),
      resources=dict(
        requests=dict(cpu=0.5, memory='40M'),
        limits=dict(cpu=1.5, memory='140M')
      )
    ))
    quota = KatQuota(create(self.res_name, ns, cpu='1', memory='50M'))
    pod.wait_until(pod.has_settled)
    quota.reload()
    self.assertEqual(0.5, quota.cpu_request_sum_deployed())
    self.assertEqual(40_000_000, quota.mem_request_sum_deployed())


def create(name, ns, **kwargs) -> V1ResourceQuota:
  return broker.coreV1.create_namespaced_resource_quota(
    namespace=ns,
    body=V1ResourceQuota(
      metadata=V1ObjectMeta(
        name=name
      ),
      spec=V1ResourceQuotaSpec(
        hard=kwargs
      )
    )
  )
