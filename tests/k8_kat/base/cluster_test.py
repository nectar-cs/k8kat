from kubernetes.client import V1Deployment, V1Service

from k8_kat.base.kube_broker import broker
from helpers.res_utils import ResUtils
from tests.k8_kat.base.k8_kat_test import K8KatTest
from utils.testing.fixtures import test_env


class ClusterTest(K8KatTest):

  @staticmethod
  def read_dep(ns, name) -> V1Deployment:
    return ResUtils.find_dp(ns, name)

  @staticmethod
  def read_svc(ns, name) -> V1Service:
    return ResUtils.find_svc(ns, name)

  @staticmethod
  def ensure_no_pods(namespaces=None):
    test_env.delete_pods(namespaces)

  @classmethod
  def setUpClass(cls) -> None:
    test_env.terraform()
    broker.connect()
    test_env.create_namespaces()

  @classmethod
  def tearDownClass(cls):
    test_env.cleanup()
