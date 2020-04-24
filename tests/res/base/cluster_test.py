import time
import unittest

from k8_kat.utils.testing.fixtures import test_env


class ClusterTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    super(ClusterTest, cls).setUpClass()
    test_env.cleanup()
    test_env.create_namespaces()
    time.sleep(2)
