import argparse
import os

from k8_kat.base.kube_broker import *
from k8_kat.dep.kat_dep import *
from utils.testing.fixtures.test_env import TestEnv
from dotenv import load_dotenv

load_dotenv()

legal_envs = ['production', 'development', 'test']
parser = argparse.ArgumentParser()
parser.add_argument('--env', '-e', help=f"Set the env: {legal_envs}")
args = parser.parse_args()

def coerce_env():
  if args.env:
    if args.env in legal_envs:
      os.environ['KAT_ENV'] = args.env
    else:
      raise Exception(f"Bad environment '{args.env}'")

def main():
  coerce_env()
  print(f"Running shell in {Utils.run_env()}")
  if Utils.is_test():
    TestEnv.terraform()
  broker.connect()

if __name__ == '__main__':
  main()
