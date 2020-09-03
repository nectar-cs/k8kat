import os
from typing import Optional

from typing_extensions import TypedDict

from k8_kat.utils.main import utils

AUTH_TYPE_IN = 'in'
AUTH_TYPE_OUT = 'out'
AUTH_TYPE_KUBE_CONF = 'default-config'
AUTH_TYPE_SKIP = 'already-authed'


class BrokerConfig(TypedDict, total=False):
  auth_type: str
  sa_name: str
  sa_ns: str
  kubectl: str
  crb_name: str
  cluster_name: str
  context: str


_prod_defaults = BrokerConfig(
  auth_type='in',
)


_dev_defaults = BrokerConfig(
  auth_type=AUTH_TYPE_KUBE_CONF,
  sa_name='nectar-dev',
  sa_ns='default',
  kubectl='kubectl',
  crb_name='nectar',
  cluster_name='dev'
)


_test_defaults = BrokerConfig(
  auth_type=AUTH_TYPE_OUT,
  sa_name='nectar-ci',
  sa_ns='default',
  kubectl="microk8s.kubectl",
  crb_name='nectar-ci',
  cluster_name='microk8s-cluster',
  context='microk8s'
)


def _load_config() -> BrokerConfig:
  if utils.is_prod():
    return _prod_defaults
  elif utils.is_dev():
    return _dev_defaults
  elif utils.is_test():
    return _test_defaults
  else:
    print(f"[broker_configs] WARN unknown env {utils.run_env()}")


def _load_value(env_var_key: str, dict_key: str) -> Optional[str]:
  env = os.environ
  default_value = _load_config().get(dict_key)
  from_specific_env = env.get(f"{utils.run_env().upper()}_{env_var_key}")
  from_global_env = env.get(env_var_key)
  return from_specific_env or from_global_env or default_value


def default_config() -> BrokerConfig:
  return BrokerConfig(
    auth_type=_load_value('CONNECT_AUTH_TYPE', 'auth_type'),
    sa_name=_load_value('CONNECT_SA_NAME', 'sa_name'),
    sa_ns=_load_value('CONNECT_SA_NS', 'sa_ns'),
    crb_name=_load_value('CONNECT_CRB_NAME', 'cbr_name'),
    kubectl=_load_value('CONNECT_KUBECTL', 'kubectl'),
    cluster_name=_load_value('CONNECT_CLUSTER', 'cluster_name'),
    context=_load_value('CONNECT_CONTEXT', 'context')
  )
