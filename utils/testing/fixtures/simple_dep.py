from kubernetes.client import V1ObjectMeta, V1PodSpec, V1Container, V1DeploymentSpec, V1PodTemplateSpec, V1LabelSelector

from k8_kat.base.kube_broker import broker

def create(**subs):
  default_labels = dict(app=subs['name'])

  deployment = broker.client.V1Deployment(
    metadata=V1ObjectMeta(
      name=subs['name'],
      labels=subs.get('labels', default_labels)
    ),
    spec=V1DeploymentSpec(
      selector=V1LabelSelector(
        match_labels=subs.get('selector', default_labels)
      ),
      template=V1PodTemplateSpec(
        metadata=V1ObjectMeta(
          labels=subs.get('labels', default_labels)
        ),
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
