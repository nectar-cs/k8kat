from typing import Dict, List

from kubernetes.client import V1PodSpec, V1Container, V1Pod, V1Scale, V1ScaleSpec

from k8_kat.auth.kube_broker import broker
from k8_kat.utils.main import res
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.pod.kat_pod import KatPod
from k8_kat.res.svc.kat_svc import KatSvc

COMMIT_KEYS = ['sha', 'branch', 'message', 'timestamp']

class KatDep(KatRes):
  def __init__(self, raw):
    super().__init__(raw)
    self.assoced_pods = None
    self.assoced_svcs = None
    self._am_dirty = raw is not None

  @property
  def kind(self):
    return "Deployment"

  @property
  def raw_pod_spec(self) -> V1PodSpec:
    return self.raw.spec.template.spec

  @property
  def raw_container_spec(self) -> V1Container:
    specs = self.raw_pod_spec.containers
    return specs[0] if len(specs) else None

  @property
  def image_name(self) -> str:
    container_spec = self.raw_container_spec
    return container_spec and container_spec.image

  @property
  def container_name(self) -> str:
    container_spec = self.raw_container_spec
    return container_spec and container_spec.name

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    return self.raw.spec.selector.match_labels or {}

  @property
  def template_labels(self):
    return self.raw.spec.template.metadata.labels or {}

  @property
  def commit(self) -> Dict[str, str]:
    every = self.raw.metadata.annotations or {}
    return dict([(k, every.get(f"commit-{k}")) for k in COMMIT_KEYS])

  @property
  def desired_replicas(self):
    return self.raw.spec.replicas

  @property
  def avail_replicas(self):
    return self.desired_replicas - self.raw.status.unavailableReplicas

  @property
  def image_pull_policy(self):
    cont_spec = self.raw_container_spec
    return cont_spec and cont_spec.image_pull_policy

  def svcs(self, force_reload=False) -> [KatSvc]:
    if force_reload or self.assoced_svcs is None:
      self.find_and_assoc_svcs()
    return self.assoced_svcs

  def pods(self, force_reload=False) -> [KatPod]:
    if force_reload or self.assoced_pods is None:
      self.find_and_assoc_pods()
    return self.assoced_pods

  def with_friends(self):
    self.find_and_assoc_pods()
    self.find_and_assoc_svcs()
    return self

  def find_and_assoc_pods(self):
    from k8_kat.res.base.k8_kat import K8Kat
    matchers = list(self.pod_select_labels.items())
    self.assoced_pods = K8Kat.pods().ns(self.ns).lbs_inc_each(matchers).go()

  def find_and_assoc_svcs(self):
    from k8_kat.res.base.k8_kat import K8Kat
    candidate_svcs = K8Kat.svcs().ns(self.ns).go()
    checker = lambda svc: res.dep_matches_svc(self.raw, svc.raw)
    self.assoced_svcs = [s for s in candidate_svcs if checker(s)]

  def assoc_pods(self, candidates: List[V1Pod]) -> None:
    checker = lambda pod: res.dep_owns_pod(self.raw, pod)
    self.assoced_pods = [KatPod(pod) for pod in candidates if checker(pod)]

  def assoc_svcs(self, candidates: [KatSvc]) -> None:
    checker = lambda svc: res.dep_matches_svc(self.raw, svc)
    self.assoced_svcs = [KatSvc(svc) for svc in candidates if checker(svc)]

  def _perform_patch_self(self):
    broker.appsV1Api.patch_namespaced_deployment(
      name=self.name,
      namespace=self.namespace,
      body=self.raw
    )

  def scale(self, replicas):
    broker.appsV1Api.patch_namespaced_deployment_scale(
      name=self.name,
      namespace=self.ns,
      body=V1Scale(
        spec=V1ScaleSpec(
          replicas=replicas
        )
      )
    )
    self._am_dirty = True

  def replace_image(self, new_image_name):
    self.raw.spec.template.spec.containers[0].image = new_image_name
    self._perform_patch_self()

  def restart_pods(self):
    remember_replicas = self.desired_replicas
    self.scale(0)
    self.scale(remember_replicas)
    self._am_dirty = True

  def __repr__(self):
    pod_ct = f"{3}/{self.desired_replicas}"
    return f"\n{self.ns}:{self.name} | {pod_ct}"

  @staticmethod
  def across_namespaces() -> List[Dict[str, str]]:
    from k8_kat.res.dep.dep_collection import KatDeps
    deps = KatDeps().not_ns('kube-system').go()
    output = []
    for name in set([dep.name for dep in deps]):
      appears_in = set([dep.ns for dep in deps if dep.name == name])
      output.append(dict(name=name, namespaces=sorted(list(appears_in))))
    return output
