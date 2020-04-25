import time
import unittest

from k8_kat.utils.testing import test_env, ci_perms


class ClusterTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    super(ClusterTest, cls).setUpClass()
    ci_perms.init_test_suite()
    test_env.cleanup()
    test_env.create_namespaces()
    time.sleep(2)
