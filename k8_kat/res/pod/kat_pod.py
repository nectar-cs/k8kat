from http.client import HTTPResponse
from typing import List, Optional, Dict, TypeVar
from functools import lru_cache, wraps

from kubernetes import stream as k8s_streaming
from kubernetes.client import V1Pod, V1Container, \
  V1ContainerState
from kubernetes.client.rest import ApiException

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.pod import pod_utils
from k8_kat.utils.main import utils, units
from k8_kat.utils.main.class_property import classproperty


Metric = TypeVar('Metric', bound=KatRes)

class KatPod(KatRes):
  def __init__(self, raw, wait_until_running=False):
    super().__init__(raw)
    if wait_until_running:
      self.wait_until_running()

# --
# --
# --
# -------------------------------PROPERTIES-------------------------------
# --
# --
# --

  def running_normally(func):
    """Note: needs to be defined at top of class."""
    @wraps(func)
    def running_normally_func(self, *args, **kwargs):
      if self.is_running_normally():
        return func(self, *args, **kwargs)
      else:
        return None

    return running_normally_func

  @classproperty
  def kind(self):
    return "Pod"

  @property
  def labels(self):
    base = super().labels
    bad_key = 'pod-template-hash'
    return {k: base[k] for k in base.keys() if k != bad_key}

  @property
  def phase(self):
    return self.body().status.phase

  @property
  def ip(self) -> str:
    return utils.try_or(lambda: self.body().status.pod_ip)

  @property
  def has_parent (self) -> bool:
    refs = self.raw.metadata.owner_references
    return refs is not None and len(refs) > 0

# --
# --
# --
# -------------------------------INTEL-------------------------------
# --
# --
# --

  def body(self) -> V1Pod:
    return self.raw

  def container(self, index=0) -> V1Container:
    return self.body().spec.containers[index]

  def image(self, index=0) -> str:
    return self.container and self.container(index).image

  def main_container_states(self) -> List[V1ContainerState]:
    statuses = self.body().status.container_statuses or []
    return [status.state for status in statuses]

  def init_container_states(self) -> List[V1ContainerState]:
    statuses = self.body().status.init_container_statuses or []
    return [status.state for status in statuses]

  def ternary_status(self) -> str:
    if self.is_working():
      return 'positive'
    elif self.is_broken():
      return 'negative'
    else:
      return 'pending'

  def is_running_normally(self):
    if self.is_running():
      main_states = self.main_container_states()
      runners = filter_states(main_states, 'running')
      return len(main_states) == len(runners)

  def is_pending_normally(self):
    return self.is_pending() and \
           not self.is_pending_morbidly()

  def is_running_morbidly(self):
    return self.is_running() and \
           not self.is_running_normally()

  def is_working(self):
    return self.is_running_normally() or \
           self.has_succeeded()

  def is_broken(self) -> bool:
    return self.is_pending_morbidly() or \
           self.is_running_morbidly() or \
           self.has_failed()

  def has_settled(self) -> bool:
    return not self.is_pending_normally()

  def is_pending_morbidly(self) -> bool:
    if self.is_pending():
      init_states = self.init_container_states()
      waiting_init = filter_states(init_states, 'waiting')
      if has_morbid_pending_reasons(waiting_init):
        return True

      main_states = self.main_container_states()
      main_init = filter_states(main_states, 'waiting')
      return has_morbid_pending_reasons(main_init)
    else:
      return False

  def is_running(self) -> bool:
    return self.body().status.phase == 'Running'

  def is_pending(self) -> bool:
    return self.body().status.phase == 'Pending'

  def has_run(self) -> bool:
    return self.body().status.phase in ['Failed', 'Succeeded']

  def has_failed(self) -> bool:
    return self.body().status.phase == 'Failed'

  def has_succeeded(self):
    return self.body().status.phase == 'Succeeded'

  def raw_logs(self, seconds=60) -> Optional[str]:
    try:
      return broker.coreV1.read_namespaced_pod_log(
        namespace=self.namespace,
        name=self.name,
        since_seconds=seconds
      )
    except ApiException:
      return None

  @running_normally
  def log_lines(self, seconds=60) -> List[str]:
    raw_log_str = self.raw_logs(seconds)
    if raw_log_str:
      return raw_log_str.strip("\n").split("\n")
    else:
      return []

  @running_normally
  def cpu_usage(self) -> Optional[float]:
    """Returns pod's total CPU usage in cores."""
    containers = self.get_pod_metrics()['containers']
    cpu_quant = [units.change_units(ctr['usage']['cpu']) for ctr in containers]
    try:
      return round(sum(cpu_quant), 3)
    except TypeError:
      return None

  @lru_cache(maxsize=128)
  def cpu_limits(self) -> Optional[float]:
    """Returns pod's total CPU limits in cores."""
    return self.get_pod_capacity('limits', 'cpu')

  @lru_cache(maxsize=128)
  def cpu_requests(self) -> Optional[float]:
    """Returns pod's total CPU requests in cores."""
    return self.get_pod_capacity('requests', 'cpu')

  @running_normally
  def memory_usage(self) -> Optional[float]:
    """Returns pod's total memory usage in bytes."""
    containers = self.get_pod_metrics()['containers']
    memory_quant = [units.change_units(ctr['usage']['memory']) for ctr in containers]
    try:
      return round(sum(memory_quant), 3)
    except TypeError:
      return None

  @lru_cache(maxsize=128)
  def memory_limits(self) -> Optional[float]:
    """Returns pod's total memory limits in bytes."""
    return self.get_pod_capacity('limits', 'memory')

  @lru_cache(maxsize=128)
  def memory_requests(self) -> Optional[float]:
    """Returns pod's total memory requests in bytes."""
    return self.get_pod_capacity('requests', 'memory')

  @running_normally
  def get_pod_metrics(self) -> Optional[Metric]:
    """Returns pod's metrics using k8s metrics API. Only for running pods."""
    return broker.custom.get_namespaced_custom_object(
      group='metrics.k8s.io',
      version='v1beta1',
      namespace=self.namespace,
      plural='pods',
      name=self.name
    )

  def get_pod_capacity(self, metrics_src: str, resource_type: str) -> Optional[float]:
    """Gets pod capacity and returns in cores (cpu) / bytes (memory)."""
    container_capacity = [
      get_container_capacity(ctr, metrics_src, resource_type)
      for ctr in self.body().spec.containers]
    try:
      return round(sum(container_capacity), 3)
    except TypeError:
      return None

# --
# --
# --
# -------------------------------ACTION-------------------------------
# --
# --
# --

  @classmethod
  def consume_runner(cls, name: str, ns: str, wait_until_gone=False) -> Optional[str]:
    pod = cls.wait_until_exists(name, ns)
    if pod:
      pod.wait_until(pod.has_run)
      logs = None
      if pod.has_succeeded():
        logs = pod.raw_logs()
      pod.delete(wait_until_gone)
      return logs
    else:
      return None

  @running_normally
  def shell_exec(self, command) -> Optional[str]:
    fmt_command = pod_utils.coerce_cmd_format(command)
    result = k8s_streaming.stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.name,
      self.namespace,
      command=fmt_command,
      stderr=True,
      stdin=False,
      stdout=True,
      tty=False
    )

    return result.strip() if result else None

  def replace_image(self, new_image_name, index=0):
    self.body().spec.containers[index].image = new_image_name
    self.patch()

  def wait_until_running(self):
    return self.wait_until(self.is_running)

  def invoke_curl(self, **kwargs) -> HTTPResponse:
    fmt_command = pod_utils.build_curl_cmd(**kwargs, with_command=True)
    result = self.shell_exec(fmt_command)
    if result is not None:
      result = pod_utils.parse_response(result)
    return result

  @classmethod
  def k8s_verb_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_pod,
      patch=broker.coreV1.patch_namespaced_pod,
      delete=broker.coreV1.delete_namespaced_pod,
      list=broker.coreV1.list_namespaced_pod
    )

  def reload(self) -> Optional['KatRes']:
    self.cpu_limits.cache_clear()
    self.cpu_requests.cache_clear()
    self.memory_limits.cache_clear()
    self.memory_requests.cache_clear()
    return super().reload()

# --
# --
# --
# -------------------------------RELATION-------------------------------
# --
# --
# --


# --
# --
# --
# -------------------------------UTILS-------------------------------
# --
# --
# --


def has_morbid_pending_reasons(states: List[V1ContainerState]):
  stated_reasons = set([state.waiting.reason for state in states])
  good_reasons = {'ContainerCreating', 'PullingImage', 'PodInitializing'}
  bad_reasons = stated_reasons - good_reasons
  return len(bad_reasons) > 0


def filter_states(states: List[V1ContainerState], _type: str) -> List[V1ContainerState]:
  return [state for state in states if getattr(state, _type)]


def get_container_capacity(ctr, metrics_src: str, resource_type: str) -> Optional[float]:
  """Gets container capacity and returns in cores (cpu) / bytes (memory)."""
  metrics_dict: Dict = getattr(ctr.resources, metrics_src, {})
  capacity_expr = metrics_dict.get(resource_type, '')
  return units.change_units(capacity_expr)