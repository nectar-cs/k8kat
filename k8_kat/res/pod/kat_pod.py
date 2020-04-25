import time

from kubernetes.client import V1PodStatus
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
    return self.raw.status.phase

  @property
  def status(self):
    return pod_utils.true_pod_state(
      self.raw.status.phase,
      self.container_status,
      False
    )

  @property
  def exit_code(self):
    return utils.try_or(lambda: self.container_state.exit_code)

  @property
  def full_status(self):
    return pod_utils.true_pod_state(
      self.raw.status.phase,
      self.container_status,
      True
    )

  @property
  def container(self):
    return self.raw.spec.containers[0]

  @property
  def container_status(self) -> V1PodStatus:
    cont_statuses = self.raw.status.container_statuses
    if cont_statuses and len(cont_statuses):
      return cont_statuses[0]
    else:
      return None

  @property
  def ip(self) -> str:
    return utils.try_or(lambda: self.raw.status.pod_ip)

  @property
  def image(self) -> str:
    return self.container and self.container.image

  @property
  def container_state(self):
    status = self.container_status
    if status:
      if status.state:
        state = status.state
        return state.running or state.waiting or state.terminated
    return None

  @property
  def updated_at(self):
    return utils.try_or(lambda: self.container_state.started_at)

  def is_running(self) -> bool:
    wtf_kubernetes = self.raw.status
    if type(wtf_kubernetes) == str:
      return wtf_kubernetes == 'Running'
    else:
      return wtf_kubernetes.phase == 'Running'

  def has_run(self) -> bool:
    return self.full_status in ['Failed', 'Succeeded']

  def delete(self, wait_until_gone=False):
    if wait_until_gone:
      while self.find_myself():
        time.sleep(0.5)

  def replace_image(self, new_image_name):
    self.raw.spec.containers[0].image = new_image_name
    self._perform_patch_self()

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

  def wait_until(self, predicate):
    condition_met = False
    for attempts in range(0, 50):
      if predicate():
        condition_met = True
        break
      else:
        time.sleep(1)
        self.reload()
    return condition_met

  def wait_until_running(self):
    return self.wait_until(self.is_running)

  def curl_into(self, to_pod, **kwargs):
    kwargs['url'] = to_pod.ip
    return self.run_curl(**kwargs)

  def run_curl(self, **kwargs):
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

  @classmethod
  def _collection_class(cls):
    from k8_kat.res.pod.pod_collection import PodCollection
    return PodCollection

  def __repr__(self):
    return f"\n{self.ns}:{self.name} | {self.image} | {self.status}"
