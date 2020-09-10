import base64

from kubernetes import config, client
import urllib3
from kubernetes.client import CoreV1Api, AppsV1Api, CustomObjectsApi, ExtensionsV1beta1Api, BatchV1Api

from k8kat.auth.broker_configs import read_env_config, BrokerConfig
from k8kat.auth.broker_configs import AUTH_TYPE_IN, AUTH_TYPE_OUT
from k8kat.auth.broker_configs import AUTH_TYPE_KUBE_CONF, AUTH_TYPE_SKIP
from k8kat.utils.main import utils


class BrokerConnException(Exception):
  def __init__(self, message):
    super().__init__(message)


class KubeBroker:

  def __init__(self):
    self.connect_config = {}
    self.is_connected = False
    self.last_error = None
    self.rbacV1 = None
    self.coreV1 = None
    self.appsV1 = None
    self.client = None
    self.extsV1 = None
    self.custom = None
    self.batchV1 = None

  def connect(self, _config: BrokerConfig = None) -> bool:
    # traceback.print_stack()
    connect_config = _config or read_env_config()
    connect_type = connect_config['auth_type']

    if connect_type == AUTH_TYPE_IN:
      outcome = self.connect_in_cluster()
    elif connect_type == AUTH_TYPE_OUT:
      outcome = self.connect_out_cluster(connect_config)
    elif connect_type == AUTH_TYPE_KUBE_CONF:
      outcome = self.connect_kube_config(connect_config)
    elif connect_type == AUTH_TYPE_SKIP:
      outcome = self.test_connected()
    else:
      outcome = None

    if outcome:
      self.load_api()

    self.is_connected = outcome
    self.connect_config = connect_config
    return outcome

  def test_connected(self) -> bool:
    return self.coreV1.read_namespaced_pod()

  def connect_or_raise(self, passed_config=None):
    if not self.connect(passed_config):
      raise Exception("Cluster authentication failed")

  def load_api(self):
    self.client = client
    self.rbacV1 = client.RbacAuthorizationV1Api()
    self.coreV1: CoreV1Api = client.CoreV1Api()
    self.appsV1: AppsV1Api = client.AppsV1Api()
    self.custom: CustomObjectsApi = client.CustomObjectsApi()
    self.extsV1: ExtensionsV1beta1Api = client.ExtensionsV1beta1Api()
    self.batchV1: BatchV1Api = client.BatchV1Api()

  def connect_in_cluster(self):
    try:
      print(f"[k8kat::kube_broker] In-cluster auth...")
      config.load_incluster_config()
      print(f"[k8kat::kube_broker] In-cluster auth success.")
      return True
    except Exception as e:
      print(f"[kube_broker] In-cluster connect Failed: {e}")
      self.last_error = e
      return False

  def connect_kube_config(self, _config: BrokerConfig):
    try:
      print("[k8kat::kube_broker] Default config auth...")
      config.load_kube_config(context=_config.get('context'))
      print("[k8kat::kube_broker] Default config auth success")
      return True
    except Exception as e:
      print(f"[kube_broker] In-cluster connect Failed: {e}")
      self.last_error = e
      return False

  def connect_out_cluster(self, _config: BrokerConfig):
    rep = _out_conn_debug_strs(_config)
    try:
      print(f"[k8kat::kube_broker] Out-cluster auth ({rep})...")
      configuration = prep_out_client_config(_config)
      client.Configuration.set_default(configuration)
      print(f"[k8kat::kube_broker] Out-cluster auth success")
      return True
    except Exception as e:
      print(f"[k8kat::kube_broker] Out-cluster auth failed {rep}")
      self.last_error = e
      return False

  def is_in_cluster_auth(self):
    return self.connect_config['auth_type'] == 'in'

  def kubectl(self):
    return self.connect_config['kubectl']

  def check_connected_or_raise(self):
    if not self.is_connected:
      if not self.connect():
        raise BrokerConnException(self.last_error or "unknown")


broker = KubeBroker()


def _out_conn_debug_strs(_config: BrokerConfig) -> str:
  context = _config.get('context')
  cluster_name = _config.get('cluster_name')
  sa_name = _config.get('sa_name')
  sa_ns = _config.get('sa_ns')
  return f"cluster={cluster_name}/{context}, perms={sa_ns}/{sa_name}"


def prep_out_client_config(_config: BrokerConfig):
  urllib3.disable_warnings()
  user_token = read_target_cluster_user_token(_config)
  configuration = client.Configuration()
  configuration.host = read_target_cluster_ip(_config)
  configuration.verify_ssl = False
  configuration.debug = False
  configuration.api_key = {"authorization": f"Bearer {user_token}"}
  return configuration


def read_target_cluster_user_token(_config: BrokerConfig) -> str:
  _config = _config
  ctx, sa_name, sa_ns = _config['context'], _config['sa_name'], _config['sa_ns']
  sa_bundle = utils.jk_exec(f"get sa/{sa_name}", ns=sa_ns, ctx=ctx)
  secret_name = sa_bundle['secrets'][0]['name']
  secret_bundle = utils.jk_exec(f"get secret/{secret_name}", ns=sa_ns, ctx=ctx)
  b64_user_token = secret_bundle['data']['token']
  out = str(base64.b64decode(b64_user_token))[2:-1]
  return out


def read_target_cluster_ip(_config: BrokerConfig) -> str:
  on_board_config = utils.jk_exec('config view')
  clusters = on_board_config['clusters']
  target = _config['cluster_name']
  cluster_bundle = [c for c in clusters if c['name'] == target][0]
  return cluster_bundle['cluster']['server']
