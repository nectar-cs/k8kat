import argparse
import os

import yaml

from k8_kat.auth.broker_configs import default_config
from k8_kat.utils.main import utils

def terraform():
  if utils.run_env() == 'production':
    raise Exception('Cannot terraform in production!')

  finder = lambda name: [rd for rd in res_defs if rd['kind'] == name][0]
  sa_name, sa_ns = [default_config()['sa_name'], default_config()['sa_ns']]
  crb_name, context = [default_config()['crb_name'], default_config()['context']]
  kubectl = default_config()['kubectl']

  message = dict(sa_name=sa_name, sa_ns=sa_ns, crb_name=crb_name)
  print(f"Terraforming context {default_config()['context']}: {message}...")

  root = utils.root_path()
  stream = open(os.path.join(root, f"utils/testing/fixtures/ci-perms.yaml"), 'r')

  res_defs = [data for data in yaml.load_all(stream, Loader=yaml.BaseLoader)]
  sa, crb = [finder('ServiceAccount'), finder('ClusterRoleBinding')]
  subject = f"system:serviceaccount:{sa_ns}:{sa_name}"

  sa['metadata']['name'] = sa_name or sa['metadata']['name']
  sa['metadata']['namespace'] = sa_ns or sa['metadata']['namespace']
  crb['metadata']['name'] = crb_name or crb['metadata']['name']
  crb['subjects'][0]['name'] = subject or crb['subjects'][0]['name']

  output = yaml.dump_all([sa, crb])

  from shlex import quote
  cmd = f"{utils.kmd('apply', k=kubectl, ctx=context)} -f -<<EOF\n{quote(output)}\nEOF"
  utils.shell_exec(cmd)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('--env', '-e', help=f"Set the env: {utils.legal_envs}")
  args = parser.parse_args()
  if args.env:
    utils.set_run_env(args.env)
  terraform()
