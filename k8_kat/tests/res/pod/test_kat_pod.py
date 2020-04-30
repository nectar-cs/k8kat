from kubernetes.client import V1Container, V1EnvVar, V1EnvVarSource, V1ConfigMapKeySelector

from k8_kat.auth.kube_broker import broker
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.testing import test_helper, ns_factory, simple_pod


class TestKatPod(Base.TestKatRes):

  # @classmethod
  # def setUpClass(cls) -> None:
  #   super(TestKatPod, cls).setUpClass()
  #   result = ns_factory.request(2)
  #   cls.n1, cls.n2 = result
  #   test_helper.create_pod(cls.n1, 'p1')
  #   test_helper.create_pod(cls.n1, 'p2')
  #   test_helper.create_pod(cls.n2, 'p1')

  @classmethod
  def res_class(cls):
    return KatPod

  def create_res(self, ns, name):
    test_helper.create_pod(ns, name)

  # def setUp(self) -> None:
  #   self.pod = KatPod.find(self.n1, 'p1')

  # def test_label(self):
  #   self.assertIsNone(self.pod.labels.get('foo'))
  #   self.pod.set_label(foo='bar')
  #   self.assertEqual(self.pod.labels.get('foo'), 'bar')
  #
  # def test_trigger(self):
  #   self.assertIsNone(self.pod.labels.get('trigger'))
  #   self.pod.trigger()
  #   self.assertIsNotNone(self.pod.labels.get('trigger'))
  #
  # def test_shell_exec(self):
  #   self.pod.wait_until_running()
  #   output = self.pod.shell_exec("echo foo").strip()
  #   self.assertEqual(output, "foo")
  #
  # def test_states(self):
  #   ns, = ns_factory.request(1)
  #   crasher(ns=ns, name='p')
  #   for i in range(20):
  #     pod = KatPod.find(ns, 'p')
  #     print(pod.body().status)


def crasher(**kwargs):
  simple_pod.create(
    cmd="not-a-real-command",
    **kwargs
  )


def puller(**kwargs):
  simple_pod.create(
    image="not-a-real-image",
    **kwargs
  )


def one_container_crasher(**kwargs):
  orig = simple_pod.pod(**kwargs)
  orig.spec.containers.append(
    V1Container(command='not-a-real-command')
  )
  broker.coreV1.create_namespaced_pod(
    body=orig,
    namespace=kwargs.get('ns')
  )


def init_crasher(**kwargs):
  orig = simple_pod.pod(**kwargs)
  orig.spec.init_containers = [
    V1Container(
      command='not-a-real-command'
    )
  ]
  broker.coreV1.create_namespaced_pod(
    body=orig,
    namespace=kwargs.get('ns')
  )


def config_map_wisher(**kwargs):
  orig = simple_pod.pod(**kwargs)
  orig.spec.containers[0].env = [
    V1EnvVar(
      name='foo',
      value_from=V1EnvVarSource(
        config_map_key_ref=V1ConfigMapKeySelector(
          name='not-a-real-map',
          key='not-a-real-key'
        )
      )
    )
  ]
  broker.coreV1.create_namespaced_pod(
    body=orig,
    namespace=kwargs.get('ns')
  )


def lengthy_terminator(**kwargs):
  simple_pod.create(
    image="nginx",
    cmd=["/bin/sh", "-c", "--"],
    args=["while true; do sleep 10; done;"],
    **kwargs
  )
