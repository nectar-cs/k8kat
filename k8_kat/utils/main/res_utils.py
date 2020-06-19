
def kat_classes():

  from k8_kat.res.config_map.kat_map import KatMap
  from k8_kat.res.dep.kat_dep import KatDep
  from k8_kat.res.ns.kat_ns import KatNs
  from k8_kat.res.pod.kat_pod import KatPod
  from k8_kat.res.pvc.kat_pvc import KatPvc
  from k8_kat.res.rbac.rbac import KatRole, KatRoleBinding, KatClusterRole, KatClusterRoleBinding
  from k8_kat.res.sa.kat_service_account import KatServiceAccount
  from k8_kat.res.secret.kat_secret import KatSecret
  from k8_kat.res.svc.kat_svc import KatSvc
  from k8_kat.res.ingress.kat_ingress import KatIngress
  from k8_kat.res.quotas.kat_quota import KatQuota
  from k8_kat.res.nodes.kat_node import KatNode
  from k8_kat.res.job.kat_job import KatJob
  from k8_kat.res.rs.kat_rs import KatRs

  return [
    KatRole,
    KatRoleBinding,
    KatClusterRole,
    KatClusterRoleBinding,
    KatServiceAccount,
    KatNs,
    KatNode,
    KatMap,
    KatSecret,
    KatPvc,
    KatPod,
    KatDep,
    KatSvc,
    KatIngress,
    KatQuota,
    KatJob,
    KatRs
  ]
