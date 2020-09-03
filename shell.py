import argparse

import dotenv

from k8_kat.auth.kube_broker import broker
from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.res.ns.kat_ns import KatNs
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.res.quotas.kat_quota import KatQuota
from k8_kat.res.rbac.rbac import KatClusterRole, KatClusterRoleBinding, KatRole, KatRoleBinding
from k8_kat.res.sa.kat_service_account import KatServiceAccount
from k8_kat.res.svc.kat_svc import KatSvc
from k8_kat.utils.main import utils


def main():
  dotenv.load_dotenv()
  print(f"Running shell in {utils.run_env()}")
  broker.connect()


if __name__ == '__main__':
  main()
