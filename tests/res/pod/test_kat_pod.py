from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.utils.testing import test_env
from tests.res.base.cluster_test import ClusterTest


class TestKatPod(ClusterTest):

  @classmethod
  def setUpClass(cls) -> None:
    super(TestKatPod, cls).setUpClass()
    test_env.create_pod('n1', 'p1')
    test_env.create_pod('n1', 'p2')
    test_env.create_pod('n2', 'p1')

  def setUp(self) -> None:
    self.pod = KatPod.find('n1', 'p1')

  def test_find_myself(self):
    self.assertEqual(self.pod.name, 'p1')
    self.assertEqual(self.pod.ns, 'n1')

  def test_shell_exec(self):
    self.pod.wait_until_running()
    output = self.pod.shell_exec("echo foo").strip()
    self.assertEqual(output, "foo")
