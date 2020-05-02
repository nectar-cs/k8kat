from typing import Dict

from kubernetes.client import V1PodSpec, V1Container, V1Scale, V1ScaleSpec, V1Deployment

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes


class KatDep(KatRes):

  @property
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
  def desired_replicas(self) -> int:
    return self.raw.spec.replicas

  @property
  def avail_replicas(self):
    return self.raw.status.available_replicas

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

  def image_pull_policy(self, index=0) -> str:
    cont_spec = self.container_spec(index)
    return cont_spec and cont_spec.image_pull_policy

  def is_running(self) -> bool:
    replicas = self.raw.status.ready_replicas
    return type(replicas) == int and replicas >= 1

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
