from typing import Any, Dict

from k8_kat.res.pod.pod_serialization import PodSerialization
from k8_kat.res.svc.svc_serialization import SvcSerialization


class DepSerialization:

  @staticmethod
  def standard(dep) -> Dict[str, Any]:
    return dict(
      name=dep.name,
      namespace=dep.namespace,
      labels=dep.labels,
      template_labels=dep.template_labels,
      selector_labels=dep.pod_select_labels,
      replicas=dep.raw.spec.replicas,
      image_name=dep.image_name,
      container_name=dep.container_name,
      commit=dep.commit,
      image_pull_policy=dep.image_pull_policy
    )

  @staticmethod
  def with_pods_and_svcs(dep) -> Dict[str, Any]:
    pod_ser = PodSerialization.standard
    svc_ser = SvcSerialization.standard

    return {
      **DepSerialization.standard(dep),
      **dict(
        pods=[pod_ser(pod) for pod in dep.pods()],
        services=[svc_ser(pod) for pod in dep.svcs()]
      )
    }

  @staticmethod
  def as_needed(dep):
    base = DepSerialization.standard(dep)
    pod_ser = PodSerialization.standard
    svc_ser = SvcSerialization.standard

    if dep.assoced_pods is not None:
      base = dict(**base, pods=[pod_ser(pod) for pod in dep.pods()])

    if dep.assoced_svcs is not None:
      base = dict(**base, services=[svc_ser(svc) for svc in dep.svcs()])

    return base
