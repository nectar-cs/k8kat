import time

from kubernetes.client import V1ObjectMeta, V1PodSpec, V1Container, V1DeploymentSpec, V1PodTemplateSpec, V1LabelSelector

from k8kat.auth.kube_broker import broker

def create(**subs):
  default_labels = dict(app=subs['name'])
  labels = {**subs.get('labels', {}), **default_labels}
  match_labels = {**labels, **subs.get('selector', {})}

  deployment = broker.client.V1Deployment(
    metadata=V1ObjectMeta(
      name=subs['name'],
      labels=labels,
      annotations=subs.get('annotations', {})
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
              name=subs.get("container", "primary"),
              image=subs.get('image', 'nginx'),
              image_pull_policy=subs.get('ipp', 'IfNotPresent'),
              resources=subs.get('resources', None)
            )
          ]
        )
      )
    )
  )

  result = broker.appsV1.create_namespaced_deployment(
    body=deployment,
    namespace=subs['ns']
  )

  eq_exprs = [f"{t[0]}={t[1]}" for t in list(labels.items())]
  def pods():
    return broker.coreV1.list_namespaced_pod(
      namespace=subs['ns'],
      label_selector=",".join(eq_exprs)
    ).items

  while not len(pods()) == deployment.spec.replicas:
    time.sleep(1)

  return result
