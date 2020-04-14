import argparse

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.k8_kat import K8Kat as Kt
from k8_kat.res.config_map.config_map_collection import ConfigMapCollection
from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.res.pod import pod_factory
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.res.config_map.kat_map import KatMap
from k8_kat.res.svc.kat_svc import KatSvc
from k8_kat.utils.main import utils
from k8_kat.utils.testing.fixtures import test_env, simple_pod

parser = argparse.ArgumentParser()
parser.add_argument('--env', '-e', help=f"Set the env: {utils.legal_envs}")
args = parser.parse_args()


def coerce_env():
  Kt.deps()
  if args.env:
    utils.set_run_env(args.env)

def main():
  coerce_env()
  print(f"Running shell in {utils.run_env()}")
  broker.connect()


if __name__ == '__main__':
  main()
