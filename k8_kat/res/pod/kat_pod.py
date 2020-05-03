from http.client import HTTPResponse
from typing import List, Optional

from kubernetes import stream as k8s_streaming
from kubernetes.client import V1Pod, V1Container, \
  V1ContainerState
from kubernetes.client.rest import ApiException

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.pod import pod_utils
from k8_kat.utils.main import utils


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

  @property
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
  def updated_at(self):
    return self.body().status.start_time

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

  def is_running_normally(self):
    if self.is_running():
      main_states = self.main_container_states()
      runners = filter_states(main_states, 'running')
      return len(main_states) == len(runners)

  def is_pending_normally(self):
    return self.is_pending() and not self.is_pending_morbidly()

  def is_running_morbidly(self):
    return self.is_running() and not self.is_running_normally()

  def is_broken(self) -> bool:
    return self.is_pending_morbidly() or self.has_failed()

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

  def log_lines(self, seconds=60) -> List[str]:
    raw_log_str = self.raw_logs(seconds)
    if raw_log_str:
      return raw_log_str.strip("\n").split("\n")
    else:
      return []

# --
# --
# --
# -------------------------------ACTION-------------------------------
# --
# --
# --

  def shell_exec(self, command) -> Optional[str]:
    result = k8s_streaming.stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.name,
      self.namespace,
      command=pod_utils.coerce_cmd_format(command),
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
  reasons = set([state.waiting.reason for state in states])
  good_reasons = {'ContainerCreating', 'PullingImage'}
  bad_reasons = reasons - good_reasons
  return len(bad_reasons) > 0

def filter_states(states: List[V1ContainerState], _type: str) -> List[V1ContainerState]:
  return [state for state in states if getattr(state, _type)]

