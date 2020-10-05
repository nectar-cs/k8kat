from functools import lru_cache
from typing import Dict, List

from kubernetes.client import V1PodSpec, V1Container, V1Scale, V1ScaleSpec, V1Deployment

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes, MetricsDict
from k8kat.res.base.label_set_expressions import label_conditions_to_expr
from k8kat.res.pod.kat_pod import KP
from k8kat.res.relation.relation import Relation
from k8kat.utils.main.class_property import classproperty


class KatDep(KatRes):

  @classproperty
  def kind(self):
    return "Deployment"

  @classproperty
  def kind_aliases(self) -> List[str]:
    return [
      *super().kind_aliases,
      'deployment.apps',  # why? seems terrible
      'deploy'
    ]

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
    from k8kat.res.pod.kat_pod import KatPod
    pods: List[KatPod] = self.pods()
    return len([p for p in pods if p.is_broken()]) > 0

  def has_settled(self) -> bool:
    from k8kat.res.pod.kat_pod import KatPod
    pods: List[KatPod] = self.pods()
    pod_settle_states = list(map(KatPod.has_settled, pods))
    return len(pods) == 0 or set(pod_settle_states) == {True}

  @lru_cache(maxsize=128)
  def load_per_pod_metrics(self) -> List[MetricsDict]:
    """Loads the appropriate metrics dict from k8s metrics API."""
    label_sel = label_conditions_to_expr(self.pod_select_labels.items(), [])
    return broker.custom.list_namespaced_custom_object(
      group='metrics.k8s.io',
      version='v1beta1',
      namespace=self.namespace,
      label_selector=label_sel,
      plural='pods'
    )['items']

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

  def pods(self, **query) -> List[KP]:
    """Selects and returns pods associated with the deployment."""
    from k8kat.res.pod.kat_pod import KatPod
    return Relation[KatPod](
      model_class=KatPod,
      ns=self.ns,
      labels=self.pod_select_labels,
      **query
    )
