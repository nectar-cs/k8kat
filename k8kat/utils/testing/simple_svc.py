from kubernetes.client import V1ObjectMeta, V1ServiceSpec, V1ServicePort
from k8kat.auth.kube_broker import broker


def create(**subs):
  default_labels = dict(app=subs['name'])
  labels = {**subs.get('labels', {}), **default_labels}
  match_labels = {**labels, **subs.get('selector', {})}

  svc = broker.client.V1Service(
    api_version='v1',
    metadata=V1ObjectMeta(
      name=subs.get('name'),
      labels=labels
    ),
    spec=V1ServiceSpec(
      type=subs.get('type', 'ClusterIP'),
      selector=match_labels,
      ports=[
        V1ServicePort(
          port=subs.get('from_port', 80),
          target_port=subs.get('to_port', 80)
        )
      ]
    )
  )

  return broker.coreV1.create_namespaced_service(
    body=svc,
    namespace=subs['ns']
  )
