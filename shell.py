import argparse

from k8_kat.base.kube_broker import broker
from k8_kat.dep.kat_dep import *
from utils.testing.fixtures import test_env
from dotenv import load_dotenv
from utils.main import utils

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument('--env', '-e', help=f"Set the env: {utils.legal_envs}")
args = parser.parse_args()

def coerce_env():
  if args.env:
    utils.set_run_env(args.env)

def main():
  coerce_env()
  print(f"Running shell in {utils.run_env()}")
  if utils.is_test():
    test_env.terraform()
  broker.connect()

if __name__ == '__main__':
  main()
