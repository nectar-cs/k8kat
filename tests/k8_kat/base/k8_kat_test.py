import unittest

from utils.main import utils


class K8KatTest(unittest.TestCase):
  @classmethod
  def setUpClass(cls) -> None:
    print(f"[k8_kat_test] Force setting run env 'test'")
    utils.set_run_env('test')
