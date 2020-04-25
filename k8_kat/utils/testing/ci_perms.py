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


def apply_perms():
  if utils.run_env() == 'production':
    raise Exception('Cannot terraform in production!')

  out_file = '/tmp/k8-kat-testing-manifest.yaml'
  sa_name, sa_ns = [default_config()['sa_name'], default_config()['sa_ns']]
  crb_name, context = [default_config()['crb_name'], default_config()['context']]
  subject = f"system:serviceaccount:{sa_ns}:{sa_name}"
  kubectl = default_config()['kubectl']

  sa_name = sa_name or 'nectar-ci'
  sa_ns = sa_ns or 'default'
  crb_name = crb_name or 'nectar-ci'

  message = dict(sa_name=sa_name, sa_ns=sa_ns, crb_name=crb_name)
  print(f"Perms for context {default_config()['context']}: {message}...")

  sa = sa_dict(name=sa_name, ns=sa_ns)
  crb = crb_dict(name=crb_name, subject=subject)

  output = yaml.dump_all([sa, crb])
  tmp_file = open(out_file, "w")
  tmp_file.write(output)
  tmp_file.close()

  command = utils.kmd(f"apply -f {out_file}", ctx=context, k=kubectl)
  print(f"Running {command}")
  utils.shell_exec(command)


def is_ready():
  return test_ready_obj['ready']


def update_readiness(readiness):
  test_ready_obj['ready'] = readiness


def init_test_suite():
  if not is_ready():
    os.environ['FLASK_ENV'] = 'test'
    os.environ['KAT_ENV'] = 'test'

    dotenv.load_dotenv()
    apply_perms()
    broker.connect_or_raise()
    update_readiness(True)
