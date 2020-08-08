import argparse
import os

import dotenv
import yaml

from k8_kat.auth.broker_configs import default_config
from k8_kat.auth.kube_broker import broker
from k8_kat.utils.main import utils

test_ready_obj = dict(ready=False)


def sa_dict(name='nectar-ci', ns='default'):
  return dict(
    apiVersion='v1',
    kind='ServiceAccount',
    metadata=dict(namespace=ns, name=name)
  )


def crb_dict(name='nectar-ci', subject=None):
  return dict(
    apiVersion='rbac.authorization.k8s.io/v1',
    kind='ClusterRoleBinding',
    metadata=dict(name=name),
    subjects=[dict(kind='User', name=subject)],
    roleRef=dict(
      kind='ClusterRole',
      name='cluster-admin',
      apiGroup='rbac.authorization.k8s.io'
    )
  )


def parse_yaml_config_file(filename, list_of_keys=None):
  with open(filename, 'r') as f:
    value = yaml.load(f.read(), Loader=yaml.FullLoader)
    if list_of_keys:
      for k in list_of_keys:
        value = value[k]
    return value


def apply_perms(sa_file=None, crb_file=None, passed_config=None):
  # priority: from file > from passed config > from env > defaults

  if not passed_config:  # can't pass mutable default args
    passed_config = {}

  if utils.run_env() == 'production':
    raise Exception('Cannot terraform in production!')
  out_file = '/tmp/k8-kat-testing-manifest.yaml'

  if sa_file:
    parsed_sa_file = parse_yaml_config_file(sa_file)
    sa_name = parsed_sa_file['metadata']['name']
    sa_ns = parsed_sa_file['metadata']['namespace']
    sa = parsed_sa_file
  else:
    sa_name = passed_config.get('sa_name', None) or default_config()['sa_name'] or 'nectar-ci'
    sa_ns = passed_config.get('sa_ns', None) or default_config()['sa_ns'] or 'default'
    sa = sa_dict(name=sa_name, ns=sa_ns)

  if crb_file:
    parsed_crb_file = parse_yaml_config_file(crb_file)
    crb_name = parsed_crb_file['metadata']['name']
    crb = parsed_crb_file
  else:
    crb_name = passed_config.get('crb_name', None) or default_config()['crb_name'] or 'nectar-ci'
    subject = f"system:serviceaccount:{sa_ns}:{sa_name}"
    crb = crb_dict(name=crb_name, subject=subject)

  context = passed_config.get('context', None) or default_config()['context']
  kubectl = passed_config.get('kubectl', None) or default_config()['kubectl']

  message = dict(sa_name=sa_name, sa_ns=sa_ns, crb_name=crb_name)
  print(f"Perms for context {default_config()['context']}: {message}...")

  with open(out_file, 'w') as f: f.write(yaml.dump_all([sa, crb]))

  command = utils.kmd(f"apply -f {out_file}", ctx=context, k=kubectl)
  print(f"Running {command}")
  utils.shell_exec(command)


def is_ready():
  return test_ready_obj['ready']


def update_readiness(readiness):
  test_ready_obj['ready'] = readiness


def init_test_suite(load_env=True):
  if not is_ready():
    os.environ['FLASK_ENV'] = 'test'
    os.environ['KAT_ENV'] = 'test'
    if load_env:
      dotenv.load_dotenv()
    apply_perms()
    broker.connect_or_raise()
    update_readiness(True)
