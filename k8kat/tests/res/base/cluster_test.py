import unittest

import dotenv

from k8kat.auth.kube_broker import broker
from k8kat.utils.main import utils
from k8kat.utils.testing import ns_factory


class ClusterTest(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    super().setUpClass()
    if not is_ready():
      dotenv.load_dotenv()
      utils.set_run_env('test')
      broker.connect()
      update_readiness(True)

  @classmethod
  def tearDownClass(cls) -> None:
    ns_factory.relinquish_all()


test_ready_obj = dict(ready=False)

def is_ready():
  return test_ready_obj['ready']


def update_readiness(readiness):
  test_ready_obj['ready'] = readiness
