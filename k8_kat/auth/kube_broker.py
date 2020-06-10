import base64

from kubernetes import config, client
import urllib3

from k8_kat.auth.broker_configs import default_config
from k8_kat.utils.main import utils


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

  def connect(self):
    self.connect_config = default_config()
    connect_in = self.connect_in_cluster
    connect_out = self.connect_out_cluster
    connect_fn = connect_in if self.is_in_cluster_auth() else connect_out
    self.is_connected = connect_fn()
    self.load_api() if self.is_connected else None
    return self.is_connected

  def connect_or_raise(self):
    if not self.connect():
      raise Exception("Cluster authentication failed")

  def load_api(self):
    self.client = client
    self.rbacV1 = client.RbacAuthorizationV1Api()
    self.coreV1 = client.CoreV1Api()
    self.appsV1 = client.AppsV1Api()
    self.custom = client.CustomObjectsApi()
    self.extsV1 = client.ExtensionsV1beta1Api()

  def connect_in_cluster(self):
    try:
      print(f"[kube_broker] In-cluster auth...")
      config.load_incluster_config()
      print(f"[kube_broker] In-cluster auth success.")
      return True
    except Exception as e:
      print(f"[kube_broker] In-cluster connect Failed: {e}")
      self.last_error = e
      return False

  def connect_out_cluster(self):
    context = self.connect_config['context']
    cluster_name = self.connect_config['cluster_name']
    sa_name = self.connect_config['sa_name']
    sa_ns = self.connect_config['sa_ns']
    rep = f"cluster={cluster_name}/{context}, perms={sa_ns}/{sa_name}"

    try:
      print(f"[kube_broker] Out-cluster auth ({rep})...")
      user_token = self.read_target_cluster_user_token()
      configuration = client.Configuration()
      configuration.host = self.read_target_cluster_ip()
      configuration.verify_ssl = False
      configuration.debug = False
      configuration.api_key = {"authorization": f"Bearer {user_token}"}
      client.Configuration.set_default(configuration)
      urllib3.disable_warnings()

      print(f"[kube_broker] Out-cluster auth success")
      return True
    except Exception as e:
      print(f"[kube_broker] Out-cluster auth failed ({sa_ns}/{sa_name}): {e}")
      self.last_error = e
      return False

  def is_in_cluster_auth(self):
    return self.connect_config['auth_type'] == 'in'

  def kubectl(self):
    return self.connect_config['kubectl']

  def read_target_cluster_ip(self):
    on_board_config = utils.jk_exec('config view')
    clusters = on_board_config['clusters']
    target = self.connect_config['cluster_name']
    cluster_bundle = [c for c in clusters if c['name'] == target][0]
    return cluster_bundle['cluster']['server']

  def read_target_cluster_user_token(self):
    _config = self.connect_config
    ctx, sa_name, sa_ns = _config['context'], _config['sa_name'], _config['sa_ns']
    sa_bundle = utils.jk_exec(f"get sa/{sa_name}", ns=sa_ns, ctx=ctx)
    secret_name = sa_bundle['secrets'][0]['name']
    secret_bundle = utils.jk_exec(f"get secret/{secret_name}", ns=sa_ns, ctx=ctx)
    b64_user_token = secret_bundle['data']['token']
    out = str(base64.b64decode(b64_user_token))[2:-1]
    return out

  def check_connected_or_raise(self):
    if not self.is_connected:
      if not self.connect():
        raise BrokerConnException(self.last_error or "unknown")


broker = KubeBroker()
