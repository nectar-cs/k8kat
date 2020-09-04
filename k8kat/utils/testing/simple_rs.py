from kubernetes.client import V1ObjectMeta, V1ReplicaSetSpec, V1LabelSelector, \
  V1PodTemplateSpec, V1PodSpec, V1Container

from k8kat.auth.kube_broker import broker


def replica_set(**subs):
  default_labels = dict(app=subs['name'])
  labels = {**subs.get('labels', {}), **default_labels}

  return broker.client.V1ReplicaSet(
    metadata=V1ObjectMeta(
      name=subs.get('name'),
      labels=labels
    ),
    spec=V1ReplicaSetSpec(
      replicas=subs.get('replicas', 1),
      selector=V1LabelSelector(
        match_labels=labels
      ),
      template=V1PodTemplateSpec(
        metadata=V1ObjectMeta(
          labels=labels
        ),
        spec=V1PodSpec(
          containers=[
            V1Container(
              name=subs.get('container', 'primary'),
              image=subs.get('image', 'nginx'),
              image_pull_policy="IfNotPresent",
              command=subs.get('command'),
              args=subs.get('args'),
              resources=subs.get('resources', None)
            )
          ]
        )
      )
    )
  )

def create(**subs):
  return broker.appsV1.create_namespaced_replica_set(
    body=replica_set(**subs),
    namespace=subs["ns"]
  )