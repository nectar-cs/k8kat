from kubernetes.client import V1JobSpec, V1ObjectMeta, V1LabelSelector, \
  V1PodTemplateSpec, V1PodSpec, V1Container

from k8kat.auth.kube_broker import broker


def job(**subs):
  default_labels = dict(app=subs['name'])
  labels = {**subs.get('labels', {}), **default_labels}

  return broker.client.V1Job(
    metadata=V1ObjectMeta(
      name=subs.get('name'),
      labels=labels
    ),
    spec=V1JobSpec(
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
              args=subs.get('args')
            )],
          restart_policy="OnFailure"
        )
      ),
      backoff_limit=4
    )
  )

def create(**subs):
  return broker.batchV1.create_namespaced_job(
    body=job(**subs),
    namespace=subs["ns"]
  )