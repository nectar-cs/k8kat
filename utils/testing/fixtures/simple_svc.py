from kubernetes.client import V1ObjectMeta, V1ServiceSpec, V1ServicePort
from k8_kat.base.kube_broker import broker


def create(**subs):
  def_labels = dict(app=subs['name'])

  svc = broker.client.V1Service(
    api_version='v1',
    metadata=V1ObjectMeta(
      name=subs.get('name'),
      labels=subs.get('labels', def_labels)
    ),
    spec=V1ServiceSpec(
      type=subs.get('type', 'ClusterIP'),
      selector=subs.get('sel_labels', def_labels),
      ports=[
        V1ServicePort(
          port=subs.get('from_port', 80),
          target_port=subs.get('to_port', 80)
        )
      ]
    )
  )

  broker.coreV1.create_namespaced_service(
    body=svc,
    namespace=subs['ns']
  )
