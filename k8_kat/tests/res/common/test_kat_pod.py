import time
from urllib.parse import quote

from kubernetes.client import V1Container, V1EnvVar, V1EnvVarSource, V1ConfigMapKeySelector

from k8_kat.auth.kube_broker import broker
from k8_kat.res.pod import pod_utils
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.tests.res.base.test_kat_res import Base
from k8_kat.utils.main import utils
from k8_kat.utils.testing import test_helper, simple_pod


class TestKatPod(Base.TestKatRes):

  @classmethod
  def res_class(cls):
    return KatPod

  @classmethod
  def create_res(cls, name, ns=None):
    return test_helper.create_pod(ns, name)

  def pre_crash_assertions(self, pod):
    self.assertFalse(pod.is_running())
    self.assertTrue(pod.is_pending())
    self.assertFalse(pod.is_running_normally())
    self.assertTrue(pod.is_pending_normally())
    self.assertFalse(pod.is_running_morbidly())
    self.assertFalse(pod.is_pending_morbidly())
    self.assertFalse(pod.has_settled())
    self.assertEqual(pod.ternary_status(), "pending")
    time.sleep(10)
    pod.reload()

  def running_morbidly_assertions(self, pod):
    self.assertTrue(pod.is_running())
    self.assertFalse(pod.is_pending())
    self.assertFalse(pod.is_running_normally())
    self.assertFalse(pod.is_pending_morbidly())
    self.assertFalse(pod.is_running_normally())
    self.assertTrue(pod.is_running_morbidly())
    self.assertTrue(pod.has_settled())
    self.assertEqual(pod.ternary_status(), "negative")

  def pending_morbidly_assertions(self, pod):
    self.assertFalse(pod.is_running())
    self.assertTrue(pod.is_pending())
    self.assertFalse(pod.is_running_normally())
    self.assertTrue(pod.is_pending_morbidly())
    self.assertFalse(pod.is_running_normally())
    self.assertFalse(pod.is_running_morbidly())
    self.assertTrue(pod.has_settled())
    self.assertEqual(pod.ternary_status(), "negative")

  def test_ternary_state(self):
    pass

  def test_states_crashing_pod(self):
    pod = create_crasher(ns=self.pns, name=self.res_name)
    self.pre_crash_assertions(pod)
    self.running_morbidly_assertions(pod)

  def test_states_image_pull_error(self):
    pod = create_puller(ns=self.pns, name=self.res_name)
    self.pre_crash_assertions(pod)
    self.pending_morbidly_assertions(pod)

  def test_init_crasher(self):
    pod = create_init_crasher(ns=self.pns, name=self.res_name)
    self.pre_crash_assertions(pod)
    self.pending_morbidly_assertions(pod)

  def test_config_map_wisher(self):
    pod = create_config_map_wisher(ns=self.pns, name=self.res_name)
    self.pre_crash_assertions(pod)
    self.pending_morbidly_assertions(pod)

  def test_healthy_pod_states(self):
    pod = KatPod(simple_pod.create(ns=self.pns, name=self.res_name))
    self.pre_crash_assertions(pod)
    pod.wait_until_running()
    self.assertEqual(pod.ternary_status(), "positive")

  def test_logs(self):
    pod = KatPod(simple_pod.create(
      ns=self.pns,
      name=self.res_name,
      image='busybox',
      command=["/bin/sh", "-c"],
      args=["echo one && echo two && exit 0"]
    ))
    pod.wait_until(pod.has_settled)
    self.assertEqual(pod.raw_logs(), "one\ntwo\n")
    self.assertEqual(pod.log_lines(), ['one', 'two'])

  def test_fmt_command(self):
    call = pod_utils.coerce_cmd_format
    actual = call(f"one two {quote('three four')}")
    self.assertEqual(actual, ["one", "two", "three four"])

  def test_shell_exec(self):
    pod = KatPod(test_helper.create_pod(self.pns, self.res_name))
    pod.wait_until_running()
    self.assertEqual(pod.shell_exec("echo foo"), "foo")
    self.assertEqual(pod.shell_exec("whoami"), "root")
    self.assertEqual(pod.shell_exec("bad-cmd"), None)

  def test_curl_from(self):
    receiver = KatPod(simple_pod.create(
      ns=self.pns,
      name=utils.rand_str(),
      image="hashicorp/http-echo",
      args=["-text", "pong"]
    ))
    sender = KatPod(simple_pod.create(
      ns=self.pns,
      name=self.res_name,
      image="ewoutp/docker-nginx-curl"
    ))
    receiver.wait_until(receiver.has_settled)
    sender.wait_until(sender.has_settled)
    ping = sender.invoke_curl(url=f"{receiver.ip}:5678")
    self.assertEqual(ping.status, 200)
    self.assertEqual(ping.read(100).decode(), 'pong')


def create_crasher(**kwargs) -> KatPod:
  return KatPod(simple_pod.create(
    command=["not-a-real-command"],
    **kwargs
  ))

def create_puller(**kwargs):
  return KatPod(simple_pod.create(
    image="not-a-real-image",
    **kwargs
  ))

def create_init_crasher(**kwargs):
  orig = simple_pod.pod(**kwargs)
  orig.spec.init_containers = [
    V1Container(
      name='doom',
      image='nginx',
      command=['not-a-real-command']
    )
  ]

  return KatPod(broker.coreV1.create_namespaced_pod(
    body=orig,
    namespace=kwargs.get('ns')
  ))


def create_config_map_wisher(**kwargs):
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

  return KatPod(broker.coreV1.create_namespaced_pod(
    body=orig,
    namespace=kwargs.get('ns')
  ))
