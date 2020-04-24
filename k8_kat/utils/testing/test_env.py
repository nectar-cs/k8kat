import argparse
import os

import yaml

from k8_kat.auth.broker_configs import default_config
from k8_kat.utils.main import utils


def finder(candidates, name):
  return [rd for rd in candidates if rd['kind'] == name][0]


def apply_perms():
  if utils.run_env() == 'production':
    raise Exception('Cannot terraform in production!')

  sa_name, sa_ns = [default_config()['sa_name'], default_config()['sa_ns']]
  crb_name, context = [default_config()['crb_name'], default_config()['context']]
  kubectl = default_config()['kubectl']

  message = dict(sa_name=sa_name, sa_ns=sa_ns, crb_name=crb_name)
  print(f"Terraforming context {default_config()['context']}: {message}...")

  root = utils.root_path()
  ci_prems_path = os.path.join(root, f"utils/testing/fixtures/ci-perms.yaml")
  stream = open(ci_prems_path, 'r')

  res_defs = [data for data in yaml.load_all(stream, Loader=yaml.BaseLoader)]
  sa, crb = [finder(res_defs, 'ServiceAccount'), finder(res_defs, 'ClusterRoleBinding')]
  subject = f"system:serviceaccount:{sa_ns}:{sa_name}"

  sa['metadata']['name'] = sa_name or sa['metadata']['name']
  sa['metadata']['namespace'] = sa_ns or sa['metadata']['namespace']
  crb['metadata']['name'] = crb_name or crb['metadata']['name']
  crb['subjects'][0]['name'] = subject or crb['subjects'][0]['name']

  output = yaml.dump_all([sa, crb])

  tmp_file = open("/tmp/k8kats.yaml", "w")
  tmp_file.write(output)
  tmp_file.close()

  command = utils.kmd("apply -f /tmp/k8kats.yaml", ctx=context, k=kubectl)
  print(f"Running {command}")
  utils.shell_exec(command)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--env', '-e', help=f"Set the env: {utils.legal_envs}")
  args = parser.parse_args()
  if args.env:
    utils.set_run_env(args.env)
  apply_perms()
