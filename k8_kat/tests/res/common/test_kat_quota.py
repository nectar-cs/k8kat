import time
from typing import Type

from kubernetes.client import V1ResourceQuota, V1ObjectMeta, V1ResourceQuotaSpec

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.res.quotas.kat_quota import KatQuota
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils
from k8_kat.utils.testing import simple_pod


class TestKatQuota(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return create(name, ns)

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatQuota

  def test_cpu_and_mem_limits(self):
    quota = KatQuota(create(self.res_name, self.pns))
    self.assertEqual(quota.cpu_limit(), 1.5)
    self.assertEqual(quota.mem_limit(), 2000000)

  def test_cpu_and_mem_usage(self):
    pod = KatPod(simple_pod.create(ns=self.pns, name=utils.rand_str()))
    quota = KatQuota(create(self.res_name, self.pns, memory='100M'))

    self.assertEqual([None, None], [quota.cpu_used(), quota.mem_used()])
    pod.wait_until_running()
    quota.reload()

    # unpredictable state in Kind CI, so just ensure not crashing
    quota.cpu_used()
    quota.mem_used()


def create(name, ns, **kwargs) -> V1ResourceQuota:
  return broker.coreV1.create_namespaced_resource_quota(
    namespace=ns,
    body=V1ResourceQuota(
      metadata=V1ObjectMeta(
        name=name
      ),
      spec=V1ResourceQuotaSpec(
        hard=dict(
          cpu=kwargs.get('cpu', '1.5'),
          memory=kwargs.get('memory', '2M')
        )
      )
    )
  )
