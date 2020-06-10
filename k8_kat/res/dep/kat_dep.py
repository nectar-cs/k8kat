from typing import Dict, List, Optional

from kubernetes.client import V1PodSpec, V1Container, V1Scale, V1ScaleSpec, V1Deployment

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.relation.relation import Relation
from k8_kat.utils.main.class_property import classproperty


class KatDep(KatRes):

  @classproperty
  def kind(self):
    return "Deployment"

  @property
  def pod_spec(self) -> V1PodSpec:
    return self.raw.spec.template.spec

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    return self.raw.spec.selector.match_labels or {}

  @property
  def template_labels(self) -> Dict[str, str]:
    return self.raw.spec.template.metadata.labels or {}

  @property
  def desired_replicas(self):
    return self.raw.spec.replicas

  @property
  def ready_replicas(self):
    return self.raw.status.ready_replicas


# --
# --
# --
# -------------------------------INTEL-------------------------------
# --
# --
# --

  def ternary_status(self):
    if self.is_running_normally():
      return 'positive'
    elif self.has_broken_pod():
      return 'negative'
    else:
      return 'pending'

  def is_running_normally(self):
    return self.ready_replicas == self.desired_replicas

  def has_broken_pod(self) -> bool:
    from k8_kat.res.pod.kat_pod import KatPod
    pods: List[KatPod] = self.pods()
    return len([p for p in pods if p.is_broken()]) > 0

  def has_settled(self) -> bool:
    from k8_kat.res.pod.kat_pod import KatPod
    pods: List[KatPod] = self.pods()
    pod_settle_states = [p.has_settled() for p in pods]
    return len(pods) == 0 or set(pod_settle_states) == {True}

  def cpu_usage(self) -> Optional[float]:
    """Returns total real-time cpu usage of a deployment in millicores."""
    try:
      return round(sum([pod.cpu_usage() for pod in self.pods()]), 1)
    except TypeError:
      return None

  def cpu_limits(self) -> Optional[float]:
    """Returns total cpu limits per deployment in millicores.
    Requires all pods to have limits defined, else returns None."""
    try:
      return round(sum([pod.cpu_limits() for pod in self.pods()]), 1)
    except TypeError:
      return None

  def cpu_requests(self) -> Optional[float]:
    """Returns total cpu requests per deployment in millicores.
    Requires all pods to have requests defined, else returns None."""
    try:
      return round(sum([pod.cpu_requests() for pod in self.pods()]), 1)
    except TypeError:
      return None

  def memory_usage(self) -> Optional[float]:
    """Returns total real-time memory usage of a deployment in Mb."""
    try:
      return round(sum([pod.memory_usage() for pod in self.pods()]), 1)
    except TypeError:
      return None

  def memory_limits(self) -> Optional[float]:
    """Returns total memory limits per deployment in Mb.
    Requires all pods to have limits defined, else returns None."""
    try:
      return round(sum([pod.memory_limits() for pod in self.pods()]), 1)
    except TypeError:
      return None

  def memory_requests(self) -> Optional[float]:
    """Returns total memory requests per deployment in Mb.
    Requires all pods to have requests defined, else returns None."""
    try:
      return round(sum([pod.memory_requests() for pod in self.pods()]), 1)
    except TypeError:
      return None

# --
# --
# --
# -------------------------------ACTION-------------------------------
# --
# --
# --

  def body(self) -> V1Deployment:
    return self.raw

  def container_spec(self, index=0) -> V1Container:
    specs = self.pod_spec.containers
    return specs[index] if len(specs) else None

  def image_name(self, index=0) -> str:
    container_spec = self.container_spec(index)
    return container_spec and container_spec.image

  def container_name(self, index=0) -> str:
    spec = self.container_spec(index)
    return spec.name if spec else None

  def ipp(self, index=0) -> str:
    cont_spec = self.container_spec(index)
    return cont_spec and cont_spec.image_pull_policy

  def replace_image(self, new_image_name):
    self.raw.spec.template.spec.containers[0].image = new_image_name
    self._perform_patch_self()

  def restart_pods(self):
    remember_replicas = self.desired_replicas
    self.scale(0)
    self.scale(remember_replicas)

  def scale(self, replicas):
    broker.appsV1.patch_namespaced_deployment_scale(
      name=self.name,
      namespace=self.ns,
      body=V1Scale(
        spec=V1ScaleSpec(
          replicas=replicas
        )
      )
    )

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.appsV1.read_namespaced_deployment,
      patch=broker.appsV1.patch_namespaced_deployment,
      delete=broker.appsV1.delete_namespaced_deployment,
      list=broker.appsV1.list_namespaced_deployment
    )

# --
# --
# --
# -------------------------------RELATIONS-------------------------------
# --
# --
# --

  def pods(self, **query):
    from k8_kat.res.pod.kat_pod import KatPod
    return Relation[KatPod](
      model_class=KatPod,
      ns=self.ns,
      labels=self.pod_select_labels,
      **query
    )

