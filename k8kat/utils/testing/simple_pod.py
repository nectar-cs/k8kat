from kubernetes.client import V1ObjectMeta, V1PodSpec, V1Container, V1ResourceRequirements

from k8kat.auth.kube_broker import broker

def pod(**subs):
  default_labels = dict(app=subs['name'])
  labels = {**subs.get('labels', {}), **default_labels}

  resource_reqs = None
  container_resources = subs.get('resources', None)
  if container_resources:
    resource_reqs = V1ResourceRequirements(**container_resources)

  return broker.client.V1Pod(
    metadata=V1ObjectMeta(
      name=subs.get('name'),
      labels=labels
    ),
    spec=V1PodSpec(
      restart_policy=subs.get('restart', 'Always'),
      containers=[
        V1Container(
          name=subs.get('container', 'primary'),
          image=subs.get('image', 'nginx'),
          image_pull_policy="IfNotPresent",
          command=subs.get('command'),
          args=subs.get('args'),
          resources=resource_reqs
        )
      ]
    )
  )


def create(**subs):
  return broker.coreV1.create_namespaced_pod(
    body=pod(**subs),
    namespace=subs['ns']
  )
