from typing import Optional, Callable


class ResourceRequester:

  def pods(self):
    raise NotImplementedError

  def cpu_request(self) -> Optional[float]:
    """Returns resource's total CPU requests in cores.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self._sum_over_pods(KatPod.cpu_request)

  def mem_limit(self) -> Optional[float]:
    """Returns resource's total memory limits in bytes.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self._sum_over_pods(KatPod.mem_limit)

  def memory_requests(self) -> Optional[float]:
    """Returns resource's total memory requests in bytes.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self._sum_over_pods(KatPod.mem_request)

  def ephemeral_storage_limits(self) -> Optional[float]:
    """Returns resource's total ephemeral storage limits in bytes.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self._sum_over_pods(KatPod.eph_storage_limit)

  def ephemeral_storage_requests(self) -> Optional[float]:
    """Returns resource's total ephemeral storage requests in bytes.
    All pods must have non-None values, else returns None."""
    from k8_kat.res.pod.kat_pod import KatPod
    return self._sum_over_pods(KatPod.eph_storage_request)

  def _sum_over_pods(self, kat_pod_method: Callable):
    quant_values = [kat_pod_method(pod) for pod in self.pods()]
    quant_values = [number for number in quant_values if number is not None]
    return sum(quant_values)
