import os
from utils.main.utils import Utils

_prod_defaults = dict(
  auth_type='in',
)

_dev_defaults = dict(
  auth_type='out',
  sa_name='nectar-dev',
  sa_ns='nectar',
  kubectl='kubectl',
  crb_name='nectar',
  cluster_name='dev'
)

_test_defaults = dict(
  auth_type='out',
  sa_name='nectar-ci',
  sa_ns='nectar',
  kubectl="microk8s.kubectl",
  crb_name='nectar-ci',
  cluster_name='microk8s-cluster',
  context='microk8s-cluster'
)

def load_config():
  if Utils.is_prod():
    return _prod_defaults
  elif Utils.is_dev():
    return _dev_defaults
  elif Utils.is_test():
    return _test_defaults
  else:
    print(f"[broker_configs] WARN unknown env {Utils.run_env()}")

def load_value(env_var_key, dict_key):
  env = os.environ
  from_mem = load_config().get(dict_key)
  from_env_env = env.get(f"{Utils.run_env().upper()}_{env_var_key}")
  from_env = env.get(env_var_key)
  return from_env_env or from_env or from_mem

def default_config():
  return dict(
    auth_type=load_value('CONNECT_AUTH_TYPE', 'auth_type'),
    sa_name=load_value('CONNECT_SA_NAME', 'sa_name'),
    sa_ns=load_value('CONNECT_SA_NS', 'sa_ns'),
    crb_name=load_value('CONNECT_CRB_NAME', 'cbr_name'),
    kubectl=load_value('CONNECT_KUBECTL', 'kubectl'),
    cluster_name=load_value('CONNECT_CLUSTER', 'cluster_name'),
    context=load_value('CONNECT_CONTEXT', 'context')
  )
