from kubernetes.client import V1ObjectMeta, V1PodSpec, V1Container

from k8_kat.base.kube_broker import broker

def create(**subs):
  default_labels = dict(app=subs['name'])
  pod = broker.client.V1Pod(
    metadata=V1ObjectMeta(
      name=subs.get('name'),
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

  return broker.coreV1.create_namespaced_pod(
    body=pod,
    namespace=subs['ns']
  )
