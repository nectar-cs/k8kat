from functools import lru_cache
from http.client import HTTPResponse
from typing import List, Optional, Callable, TypeVar, Any

from kubernetes import stream as k8s_streaming
from kubernetes.client import V1Pod, V1Container, \
  V1ContainerState, V1PodCondition
from kubernetes.client.rest import ApiException

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes, MetricsDict
from k8kat.res.events.kat_event import KatEvent
from k8kat.res.pod import pod_utils
from k8kat.res.pod.pod_utils import when_running_normally
from k8kat.utils.main import utils
from k8kat.utils.main.class_property import classproperty
from k8kat.utils.main.types import IntelDict

Fn = TypeVar('Fn', bound=Callable[..., Any])
KP = TypeVar('KP')


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
  def has_parent(self) -> bool:
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

# --
# --
# --
# -------------------------------STATE-------------------------------
# --
# --
# --

  def ternary_status(self) -> str:
    if self.is_old_enough_to_call():
      if self.is_working():
        return 'positive'
      elif self.is_broken():
        return 'negative'
    return 'pending'

  def is_old_enough_to_call(self) -> bool:
    return self.seconds_existed() > 2

  def is_running_normally(self) -> bool:
    if self.is_running():
      main_states = self.main_container_states()
      runners = self.filter_container_states(main_states, 'running')
      return len(main_states) == len(runners)

  def is_pending_normally(self) -> bool:
    return self.is_pending() and \
           not self.is_terminating() and \
           not self.is_pending_morbidly()

  def is_running_morbidly(self) -> bool:
    return self.is_running() and \
           not self.is_terminating() and \
           not self.is_running_normally()

  def is_working(self) -> bool:
    return self.is_running_normally() or \
           self.has_succeeded()

  def is_broken(self) -> bool:
    return self.is_pending_morbidly() or \
           self.is_running_morbidly() or \
           self.has_failed()

  def is_terminating(self) -> bool:
    states = self.main_container_states()
    terminators = self.filter_container_states(states, 'terminated')
    return len(terminators) > 0

  def has_settled(self) -> bool:
    return not self.is_pending_normally()

  def did_scheduling_fail(self):
    lifecycle_conditions = self.body().status.conditions
    return self.cond_has_scheduling_failed(lifecycle_conditions)

  def is_pending_morbidly(self) -> bool:
    """Whether this pod is pending because one or more container is failing to start."""
    if self.is_pending():

      if self.did_scheduling_fail():
        return True

      init_states = self.init_container_states()
      waiting_init = self.filter_container_states(init_states, 'waiting')
      if len(self.morbid_pending_reasons(waiting_init)) > 0:
        return True

      main_states = self.main_container_states()
      waiting_main = self.filter_container_states(main_states, 'waiting')
      if len(self.morbid_pending_reasons(waiting_main)):
        return True

      return False
    else:
      return False

  def is_running(self) -> bool:
    """Whether this pod is in the Running state"""
    return self.body().status.phase == 'Running'

  def is_pending(self) -> bool:
    """Whether this pod is in the Pending state"""
    return self.body().status.phase == 'Pending'

  def has_failed(self) -> bool:
    """Whether this pod is in the Failed state"""
    return self.body().status.phase == 'Failed'

  def has_succeeded(self):
    """Whether this pod is in the Succeeded state"""
    return self.body().status.phase == 'Succeeded'

  def has_run(self) -> bool:
    """Whether this pod is in the Failed or Succeeded state"""
    return self.has_failed() or self.has_succeeded()

  def raw_logs(self, seconds=60) -> Optional[str]:
    try:
      return broker.coreV1.read_namespaced_pod_log(
        namespace=self.namespace,
        name=self.name,
        since_seconds=seconds
      )
    except ApiException:
      return None

  def clean_logs(self, seconds=60) -> str:
    _raw_logs = self.raw_logs(seconds)
    return (_raw_logs or '').strip()

  def log_lines(self, seconds=60) -> List[str]:
    raw_log_str = self.raw_logs(seconds)
    if raw_log_str:
      return raw_log_str.strip("\n").split("\n")
    else:
      return []

# --
# --
# --
# ---------------------------REQ / LIM / METRICS---------------------------
# --
# --
# --

  def cpu_request(self) -> float:
    """Returns pod's total memory limits in bytes."""
    return self.read_resources_req_or_lim('requests', 'cpu')

  def cpu_limit(self) -> float:
    """Returns pod's total memory limits in bytes."""
    return self.read_resources_req_or_lim('limits', 'cpu')

  def mem_limit(self) -> float:
    """Returns pod's total memory limits in bytes."""
    return self.read_resources_req_or_lim('limits', 'memory')

  def mem_request(self) -> float:
    """Returns pod's total memory requests in bytes."""
    return self.read_resources_req_or_lim('requests', 'memory')

  def eph_storage_limit(self) -> float:
    """Returns pod's total ephemeral storage limits in bytes."""
    return self.read_resources_req_or_lim('limits', 'ephemeral-storage')

  def eph_storage_request(self) -> float:
    """Returns pod's total ephemeral storage requests in bytes."""
    return self.read_resources_req_or_lim('requests', 'ephemeral-storage')

  def read_resources_req_or_lim(self, metric: str, resource: str) -> float:
    """Fetches pod's total resource capacity (either limits or requests)
    for either CPU (cores) or memory (bytes)."""
    def container_level_value(container):
      return pod_utils.container_req_or_lim(container, metric, resource) or 0
    containers = self.body().spec.containers or []
    return sum(list(map(container_level_value, containers)))

  @when_running_normally
  @lru_cache(maxsize=128)
  def load_per_pod_metrics(self) -> Optional[List[MetricsDict]]:
    """Loads the appropriate metrics dict from k8s metrics API."""
    try:
      self_metrics = broker.custom.get_namespaced_custom_object(
        group='metrics.k8s.io',
        version='v1beta1',
        namespace=self.namespace,
        plural='pods',
        name=self.name
      )
      return [self_metrics] if self_metrics else None
    except ApiException:
      return []

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

  @when_running_normally
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

  def intel(self) -> List[IntelDict]:
    if self.is_broken():
      return [
        *self.bad_events_intel(),
        *self.running_morbidly_intel(),
        *self.bad_events_intel()
      ]
    else:
      return []

  def running_morbidly_intel(self) -> List[IntelDict]:
    return []

  def condition_status_intel(self):
    intel = []
    for cond in self.body().status.conditions or []:
      if cond.status == 'False':
        intel.append(IntelDict(
          type='StatusCondition',
          status=cond.reason,
          message=cond.message
        ))
    return intel

  def container_status_intel(self):
    bad_states: List[V1ContainerState] = self.filter_container_states([
      *self.init_container_states(),
      *self.main_container_states()
    ], 'waiting')

    intel = []
    for state in bad_states:
      intel.append(IntelDict(
        type='ContainerStatus',
        message=state.waiting.message,
        status=state.waiting.reason
      ))

    return intel

  def bad_events_intel(self) -> List[IntelDict]:
    bad_events = list(filter(KatEvent.is_failure, self.events()))
    return list(map(KatEvent.intel_bundle, bad_events))

# --
# --
# --
# -------------------------------UTILS-------------------------------
# --
# --
# --

  def main_container_states(self) -> List[V1ContainerState]:
    statuses = self.body().status.container_statuses or []
    return [status.state for status in statuses]

  def init_container_states(self) -> List[V1ContainerState]:
    statuses = self.body().status.init_container_statuses or []
    return [status.state for status in statuses]

  @staticmethod
  def cond_has_scheduling_failed(conditions: List[V1PodCondition]) -> bool:
    def finder(name: str):
      pred = lambda c: c.type == name
      return next(filter(pred, conditions or []), None)

    relevant_cond = finder('PodScheduled')
    return relevant_cond and relevant_cond.status == 'False'

  @staticmethod
  def morbid_pending_reasons(states: List[V1ContainerState]):
    stated_reasons = set([state.waiting.reason for state in states])
    good_reasons = {'ContainerCreating', 'PullingImage', 'PodInitializing'}
    return stated_reasons - good_reasons

  @staticmethod
  def filter_container_states(states: List, _type: str) -> List[V1ContainerState]:
    return [state for state in states if getattr(state, _type)]
