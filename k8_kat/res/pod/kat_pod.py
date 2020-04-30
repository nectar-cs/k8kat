from typing import Optional, List

from kubernetes.client import V1PodStatus, V1Pod, V1Container, V1ContainerStatus, V1ContainerState
from kubernetes.client.rest import ApiException
from kubernetes import stream as k8s_streaming

from k8_kat.auth.kube_broker import broker
from k8_kat.res.pod import pod_utils
from k8_kat.utils.main import res
from k8_kat.res.base.kat_res import KatRes
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
  def container(self) -> V1Container:
    return self.body().spec.containers[0]

  @property
  def container_status(self) -> Optional[V1PodStatus]:
    cont_statuses = self.body().status.container_statuses
    if cont_statuses and len(cont_statuses):
      return cont_statuses[0]
    else:
      return None

  @property
  def ip(self) -> str:
    return utils.try_or(lambda: self.body().status.pod_ip)

  @property
  def image(self) -> str:
    return self.container and self.container.image

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
    return self.body()

  def main_container_states(self) -> List[V1ContainerState]:
    statuses = self.body().status.container_statuses
    return [status.state for status in statuses]

  def init_container_states(self) -> List[V1ContainerState]:
    statuses = self.body().status.init_container_statuses
    return [status.state for status in statuses]

  def is_working(self):
    if self.is_running():
      main_states = self.main_container_states()
      runners = filter_states(main_states, 'running')
      return len(main_states) == len(runners)

  def is_broken(self) -> bool:
    return self.is_pending_morbidly() or self.is_failed()

  def has_settled(self) -> bool:
    return self.is_working() or self.is_broken()

  def is_pending_morbidly(self) -> bool:
    if self.is_pending():
      init_states = self.init_container_states()
      waiting_init = filter_states(init_states, 'waiting')
      if has_morbid_reasons(waiting_init):
        return False

      main_states = self.main_container_states()
      main_init = filter_states(main_states, 'waiting')
      return has_morbid_reasons(main_init)
    else:
      return False

  def is_running(self) -> bool:
    return self.body().status.phase == 'Running'

  def is_pending(self) -> bool:
    return self.body().status.phase == 'Pending'

  def is_failed(self):
    return self.body().status.phase == 'Failed'

  def has_run(self) -> bool:
    return self.body().status.phase in ['Failed', 'Succeeded']

  def has_failed(self) -> bool:
    return self.body().status.phase == 'Failed'

  def is_terminating(self):
    print("IMPLEMENT ME")
    raise NotImplementedError

  def raw_logs(self, seconds=60):
    return broker.coreV1.read_namespaced_pod_log(
      namespace=self.namespace,
      name=self.name,
      since_seconds=seconds
    )

  def logs(self, seconds=60):
    try:
      log_dump = self.raw_logs(seconds)
      log_lines = log_dump.split("\n")
      return [res.try_clean_log_line(line) for line in log_lines]
    except ApiException:
      return None

# --
# --
# --
# -------------------------------ACTION-------------------------------
# --
# --
# --

  def shell_exec(self, command):
    return k8s_streaming.stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.name,
      self.namespace,
      command=pod_utils.coerce_cmd_format(command),
      stderr=True,
      stdin=False,
      stdout=True,
      tty=False
    )

  def replace_image(self, new_image_name):
    self.body().spec.containers[0].image = new_image_name
    self._perform_patch_self()

  def wait_until_running(self):
    return self.wait_until(self.is_running)

  def wait_until_settled(self):
    return self.wait_until(self.is_running)

  def curl_to_other_pod(self, to_pod, **kwargs):
    kwargs['url'] = to_pod.ip
    return self.invoke_curl(**kwargs)

  def invoke_curl(self, **kwargs):
    fmt_command = pod_utils.build_curl_cmd(**kwargs)
    result = self.shell_exec(fmt_command)
    if result is not None:
      result = pod_utils.parse_response(result)
    return result

  @classmethod
  def _api_methods(cls):
    return dict(
      read=broker.coreV1.read_namespaced_pod,
      patch=broker.coreV1.patch_namespaced_pod,
      delete=broker.coreV1.delete_namespaced_pod
    )

  def __repr__(self):
    return f"\n{self.ns}:{self.name} | {self.image}"


def has_morbid_reasons(states: List[V1ContainerState]):
  reasons = set([state.waiting.reason for state in states])
  good_reasons = {'ContainerCreating', 'PullingImage'}
  bad_reasons = reasons - good_reasons
  return len(bad_reasons) > 0

def filter_states(states: List[V1ContainerState], _type: str) -> List[V1ContainerState]:
  return [state for state in states if getattr(state, _type)]




