
class PodSerialization:
  @staticmethod
  def standard(pod):
    return dict(
      name=pod.name,
      namespace=pod.namespace,
      state=pod.status,
      ip=pod.ip,
      updated_at=pod.updated_at,
      image_name=pod.image,
      labels=pod.labels
    )
