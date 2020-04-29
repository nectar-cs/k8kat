from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.tests.res.base.cluster_test import ClusterTest
from k8_kat.utils.testing import test_env, ns_factory


class TestKatPod(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatPod, cls).setUpClass()
    result = ns_factory.request(2)
    cls.n1, cls.n2 = result
    test_env.create_pod(cls.n1, 'p1')
    test_env.create_pod(cls.n1, 'p2')
    test_env.create_pod(cls.n2, 'p1')

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()

  @classmethod
  def kat_res(cls):
    return KatPod

  def setUp(self) -> None:
    self.pod = KatPod.find(self.n1, 'p1')

  def test_find_myself(self):
    self.assertEqual(self.pod.name, 'p1')
    self.assertEqual(self.pod.ns, self.n1)

  def test_shell_exec(self):
    self.pod.wait_until_running()
    output = self.pod.shell_exec("echo foo").strip()
    self.assertEqual(output, "foo")


