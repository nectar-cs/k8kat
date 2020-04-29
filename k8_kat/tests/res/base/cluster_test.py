import time
import unittest

from k8_kat.utils.testing import test_env, ci_perms, ns_factory


class ClusterTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    super(ClusterTest, cls).setUpClass()
    ci_perms.init_test_suite(load_env=True)
    # test_env.cleanup()
    # test_env.create_namespaces()
    time.sleep(2)

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()
