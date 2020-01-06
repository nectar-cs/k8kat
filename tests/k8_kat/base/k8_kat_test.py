import unittest
from kubernetes.client import V1Deployment, V1Service

from k8_kat.base.kube_broker import broker
from helpers.res_utils import ResUtils
from utils.testing.fixtures.test_env import TestEnv


class K8katTest(unittest.TestCase):

  @staticmethod
  def read_dep(ns, name) -> V1Deployment:
    return ResUtils.find_dp(ns, name)

  @staticmethod
  def read_svc(ns, name) -> V1Service:
    return ResUtils.find_svc(ns, name)

  @staticmethod
  def ensure_no_pods(namespaces=None):
    TestEnv.delete_pods(namespaces)

  @classmethod
  def setUpClass(cls) -> None:
    TestEnv.terraform()
    broker.connect()
    TestEnv.create_namespaces()

  @classmethod
  def tearDownClass(cls):
    TestEnv.cleanup()


me = K8katTest
