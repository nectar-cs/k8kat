import time

from k8kat.res.dep.kat_dep import KatDep
from k8kat.res.pod.kat_pod import KatPod
from k8kat.tests.res.base.test_kat_res import Base
from k8kat.utils.main import utils
from k8kat.utils.testing import simple_dep
from k8kat.utils.testing.simple_dep import create


class TestKatDep(Base.TestKatRes):

  @classmethod
  def res_class(cls):
    return KatDep

  @classmethod
  def create_res(cls, name, ns=None):
    return simple_dep.create(ns=ns, name=name)

  def test_annotate(self,  wait_sec=2):
    pass

  def test_bad_to_good_state_progression(self):
    dep = KatDep(simple_dep.create(
      ns=self.pns,
      name=self.res_name,
      image='bullshit-asd-x12'
    ))
    i = 0

    def pod_statuses():
      return [f"{p.name}[{p.ternary_status()}]" for p in dep.pods()]

    while i in range(20):
      dep.reload()
      print(f"{dep.ternary_status()} {pod_statuses()} {dep.seconds_existed()}")
      time.sleep(1)
      if not dep.ternary_status() == 'pending':
        break
    print("PHASE 2")
    print(f"{dep.ternary_status()} {pod_statuses()} {dep.seconds_existed()}")
    time.sleep(4)

    first_pod: KatPod = dep.pods()[0]
    dep.replace_image("nginx")

    while i in range(20):
      dep.reload()
      first_pod.reload()
      print(f"{dep.ternary_status()} {pod_statuses()} {dep.seconds_existed()}")
      time.sleep(1)
      if not dep.body():
        break
      # if dep.is_terminating():
      #   print(f"am terminating {dep.is_terminating()}")

  def test_good_to_bad_state_progression(self):
    dep = KatDep(simple_dep.create(
      ns=self.pns,
      name=self.res_name,
      image='nginx'
    ))
    i = 0

    def pod_statuses():
      return [f"{p.name}[{p.ternary_status()}]" for p in dep.pods()]

    while i in range(20):
      dep.reload()
      print(f"{dep.ternary_status()} {pod_statuses()} {dep.seconds_existed()}")
      time.sleep(1)
      if not dep.ternary_status() == 'pending':
        break

    print("PHASE 2")
    print(f"{dep.ternary_status()} {pod_statuses()} {dep.seconds_existed()}")
    time.sleep(4)

    first_pod: KatPod = dep.pods()[0]
    dep.replace_image("bullshit-asd-x12")

    while i in range(20):
      dep.reload()
      first_pod.reload()
      print(f"{dep.ternary_status()} {pod_statuses()} {dep.seconds_existed()}")
      time.sleep(1)
      if not dep.body():
        break
      # if dep.is_terminating():
      #   print(f"am terminating {dep.is_terminating()}")

  def test_image_name(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, image='busybox'))
    self.assertEqual("busybox", dep.image_name())

  def test_image_pull_policy(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, ipp='Always'))
    self.assertEqual("Always", dep.ipp())

  def test_ternary_state(self):
    pass

  def test_ternary_state_positive(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, replicas=2))
    self.assertEqual('pending', dep.ternary_status())
    dep.wait_until(dep.is_running_normally)
    time.sleep(4)
    self.assertEqual('positive', dep.ternary_status())

  def test_ternary_state_negative(self):
    dep = KatDep(create(ns=self.pns, name=self.res_name, image='bro-ken'))
    dep.wait_until(dep.has_settled)
    self.assertEqual('negative', dep.ternary_status())
    self.assertGreater(len(dep.intel()), 0)

  def test_pods(self):
    def make():
      dep = KatDep(create(ns=self.pns, name=utils.rand_str(), replicas=2))
      return dep.wait_until(dep.is_running_normally) and dep

    d1, d2 = make(), make()

    p1, p2 = d1.pods()
    self.assertIn(d1.name, p1.name)
    self.assertIn(d1.name, p2.name)

    p1, p2 = d2.pods()
    self.assertIn(d2.name, p1.name)
    self.assertIn(d2.name, p2.name)

  def gen_res_with_capped_pods(self, ns, name):
    one_pod_requests = dict(memory="25M", cpu="0.125")
    one_pod_limits = dict(memory="0.05G", cpu="0.25")
    resources = dict(requests=one_pod_requests, limits=one_pod_limits)
    raw_dep = simple_dep.create(ns=ns, name=name, replicas=2, resources=resources)
    return KatDep(raw_dep)

  def gen_mock_usage_metrics(self):
    return [
      dict(containers=[
        dict(name='x', usage=dict(cpu='250m', memory='0.25G')),
        dict(name='y', usage=dict(cpu='0.25', memory='750M'))
      ]),
      dict(containers=[
        dict(name='x', usage=dict(cpu='500m', memory=None)),
        dict(name='y', usage=dict(memory=None))
      ])
    ]
