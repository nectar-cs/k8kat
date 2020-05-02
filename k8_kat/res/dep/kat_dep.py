from typing import Dict

from kubernetes.client import V1PodSpec, V1Container, V1Scale, V1ScaleSpec

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes

COMMIT_KEYS = ['sha', 'branch', 'message', 'timestamp']

class KatDep(KatRes):

  @property
  def kind(self):
    return "Deployment"

  @property
  def pod_spec(self) -> V1PodSpec:
    return self.raw.spec.template.spec

  @property
  def raw_container_spec(self) -> V1Container:
    specs = self.pod_spec.containers
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
  def desired_replicas(self):
    return self.raw.spec.replicas

  @property
  def avail_replicas(self):
    return self.desired_replicas - self.raw.status.unavailableReplicas

  @property
  def image_pull_policy(self):
    cont_spec = self.raw_container_spec
    return cont_spec and cont_spec.image_pull_policy

  def is_running(self):
    replicas = self.raw.status.ready_replicas
    return type(replicas) == int and replicas > 0

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
  def _api_methods(cls):
    return dict(
      read=broker.appsV1.read_namespaced_deployment,
      patch=broker.appsV1.patch_namespaced_deployment,
      delete=broker.appsV1.delete_namespaced_deployment,
    )
