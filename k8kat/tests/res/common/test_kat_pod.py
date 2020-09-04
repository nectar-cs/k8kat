import time
from urllib.parse import quote

from kubernetes.client import V1Container, V1EnvVar, V1EnvVarSource, V1ConfigMapKeySelector

from k8kat.auth.kube_broker import broker
from k8kat.res.pod import pod_utils
from k8kat.res.pod.kat_pod import KatPod
from k8kat.tests.res.base.test_kat_res import Base
from k8kat.utils.main import utils
from k8kat.utils.main.utils import deep_merge
from k8kat.utils.testing import test_helper, simple_pod


class TestKatPod(Base.TestKatRes):

  @classmethod
  def res_class(cls):
    return KatPod

  @classmethod
  def create_res(cls, name, ns=None, **subs):
    return test_helper.create_pod(ns, name, **subs)

# --
# --
# --
# -------------------------------STATE LOGIC TESTS-------------------------------
# --
# --
# --

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

  # def test_init_crasher(self):
  #   pod = create_init_crasher(ns=self.pns, name=self.res_name)
  #   self.pre_crash_assertions(pod)
  #   self.pending_morbidly_assertions(pod)

  def test_config_map_wisher(self):
    pod = create_config_map_wisher(ns=self.pns, name=self.res_name)
    self.pre_crash_assertions(pod)
    self.pending_morbidly_assertions(pod)

  def test_healthy_pod_states(self):
    pod = KatPod(simple_pod.create(ns=self.pns, name=self.res_name))
    self.pre_crash_assertions(pod)
    pod.wait_until_running()
    self.assertEqual(pod.ternary_status(), "positive")

# --
# --
# --
# ----------------------------MISC TESTS----------------------------
# --
# --
# --

  def test_logs(self):
    pod = self.busybox_pod("echo one && echo two && exit 0")
    pod.wait_until(pod.has_settled)
    self.assertEqual(pod.raw_logs(), "one\ntwo\n")
    self.assertEqual(pod.log_lines(), ['one', 'two'])

  def test_consume_runner_good_cmd(self):
    self.busybox_pod("echo one && exit 0")
    result = KatPod.consume_runner(self.res_name, self.pns, True)
    self.assertEqual("one\n", result)
    self.assertIsNone(KatPod.find(self.res_name, self.pns))

  def test_consume_runner_bad_cmd(self):
    self.busybox_pod("echo one && exit 1")
    result = KatPod.consume_runner(self.res_name, self.pns, True)
    self.assertIsNone(result)
    self.assertIsNone(KatPod.find(self.res_name, self.pns))

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

# --
# --
# --
# -------------------------REQ / LIM TESTS--------------------------
# --
# --
# --

  def gen_mock_usage_metrics(self):
    return [
      dict(containers=[
        dict(name='x', usage=dict(cpu='750m', memory='0.25G')),
        dict(name='y', usage=dict(cpu='0.25', memory='750M')),
        dict(name='z'),
        None
      ])
    ]

  def test_cpu_requests_and_limits(self):
    p1 = self.reqs_pod(requests=dict(cpu="100m"), limits=dict(cpu="1"))
    self.assertEqual(p1.cpu_request(), 0.1)
    self.assertEqual(p1.cpu_limit(), 1.0)

  def test_mem_requests_and_limits(self):
    p1 = self.reqs_pod(requests=dict(memory="50M"), limits=dict(memory="0.1G"))
    self.assertEqual(p1.mem_request(), 50_000_000)
    self.assertEqual(p1.mem_limit(), 100_000_000)

  def test_requests_and_limits_with_undefined(self):
    p1 = KatPod(simple_pod.create(ns=self.pns, name=utils.rand_str()), True)
    self.assertEqual(p1.cpu_request(), None)
    self.assertEqual(p1.cpu_limit(), None)
    self.assertEqual(p1.mem_request(), None)
    self.assertEqual(p1.mem_limit(), None)
    self.assertEqual(p1.eph_storage_request(), None)
    self.assertEqual(p1.eph_storage_limit(), None)

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

# --
# --
# --
# -------------------------------ASSERTION HELPERS-------------------------------
# --
# --
# --

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

# --
# --
# --
# -------------------------------POD FAB-------------------------------
# --
# --
# --

  def reqs_pod(self, **reqs) -> KatPod:
    defaults = dict(
      requests=dict(memory="50Mi", cpu="100m"),
      limits=dict(memory="2E", cpu="2000m")
    )

    pod = KatPod(simple_pod.create(
      ns=self.pns,
      name=utils.rand_str(),
      image='nginx',
      resources=deep_merge(defaults, reqs)
    ))

    pod.wait_until_running()

    return pod

  def busybox_pod(self, args) -> KatPod:
    return KatPod(simple_pod.create(
      ns=self.pns,
      name=self.res_name,
      restart='Never',
      image='busybox',
      command=["/bin/sh", "-c"],
      args=[args]
    ))

# --
# --
# --
# -------------------------------RAW POD FAB-------------------------------
# --
# --
# --


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
