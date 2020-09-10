import argparse

import dotenv

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes
from k8kat.res.dep.kat_dep import KatDep
from k8kat.res.ns.kat_ns import KatNs
from k8kat.res.pod.kat_pod import KatPod
from k8kat.res.quotas.kat_quota import KatQuota
from k8kat.res.rbac.rbac import KatClusterRole, KatClusterRoleBinding, KatRole, KatRoleBinding
from k8kat.res.sa.kat_service_account import KatServiceAccount
from k8kat.res.svc.kat_svc import KatSvc
from k8kat.utils.main import utils

def main():
  dotenv.load_dotenv()
  print(f"Running shell in {utils.run_env()}")
  broker.connect()


if __name__ == '__main__':
  main()
