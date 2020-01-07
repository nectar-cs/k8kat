from kubernetes.client import V1ObjectMeta, V1PodSpec, V1Container, V1DeploymentSpec, V1PodTemplateSpec, V1LabelSelector

from k8_kat.base.kube_broker import broker
from k8_kat.base.label_set_expressions import LabelLogic


def create(**subs):
  default_labels = dict(app=subs['name'])
  labels = {**subs.get('labels', {}), **default_labels}
  match_labels = {**labels, **subs.get('selector', {})}

  deployment = broker.client.V1Deployment(
    metadata=V1ObjectMeta(
      name=subs['name'],
      labels=labels
    ),
    spec=V1DeploymentSpec(
      replicas=subs.get('replicas', 1),
      selector=V1LabelSelector(
        match_labels=match_labels
      ),
      template=V1PodTemplateSpec(
        metadata=V1ObjectMeta(labels=labels),
        spec=V1PodSpec(
          containers=[
            V1Container(
              name="primary",
              image=subs.get('image', 'nginx'),
              image_pull_policy="Always"
            )
          ]
        )
      )
    )
  )

  return broker.appsV1Api.create_namespaced_deployment(
    body=deployment,
    namespace=subs['ns']
  )
