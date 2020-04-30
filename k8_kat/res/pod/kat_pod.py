from typing import Optional, List

from kubernetes.client import V1PodStatus, V1Pod, V1Container, V1ContainerStatus
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

  def is_running(self) -> bool:
    wtf_kubernetes = self.body().status.phase
    if type(wtf_kubernetes) == str:
      return wtf_kubernetes == 'Running'
    else:
      return wtf_kubernetes.phase == 'Running'

  def container_reasons(self, _type: str) -> List[str]:
    main_statuses = self.body().status.container_statuses
    init_statuses = self.body().status.init_container_statuses

    def reason(container_status: V1ContainerStatus) -> Optional[str]:
      return getattr(container_status.state, _type).reason

    return [reason(status) for status in main_statuses + init_statuses]

  def has_settled(self) -> bool:
    return self.is_running() or self.is_screwed()

  def is_screwed(self) -> bool:
    if self.is_pending():
      reasons = [r for r in self.container_reasons('waiting') if r]
      return len(reasons) > 0
    return False

  def is_pending(self) -> bool:
    return self.body().status.phase == 'Pending'

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
