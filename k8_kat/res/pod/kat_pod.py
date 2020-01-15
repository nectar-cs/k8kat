from kubernetes.client.rest import ApiException
from kubernetes import stream as k8s_streaming

from k8_kat.auth.kube_broker import broker
from k8_kat.res.pod import pod_utils
from k8_kat.utils.main import res
from k8_kat.res.base.kat_res import KatRes
from k8_kat.utils.main import utils


class KatPod(KatRes):
  def __init__(self, raw):
    super().__init__(raw)

  @property
  def kind(self):
    return "Pod"

  @property
  def labels(self):
    base = super().labels
    bad_key = 'pod-template-hash'
    return {k: base[k] for k in base.keys() if k != bad_key}

  @property
  def status(self):
    return pod_utils.true_pod_state(
      self.raw.status.phase,
      self.container_status,
      False
    )

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
  def container_status(self):
    return self.raw.status.container_statuses[0]

  @property
  def ip(self):
    return utils.try_or(lambda: self.raw.status.pod_ip)

  @property
  def image(self):
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

  @property
  def is_running(self):
    return self.status == 'Running'

  @property
  def wtf(self):
    return 'coming soon!'

  def delete(self):
    broker.coreV1.delete_namespaced_pod(
      namespace=self.namespace,
      name=self.name
    )

  def _perform_patch_self(self):
    broker.coreV1.patch_namespaced_pod(
      name=self.name,
      namespace=self.namespace,
      body=self.raw
    )

  def replace_image(self, new_image_name):
    self.raw.spec.containers[0].image = new_image_name
    self._perform_patch_self()

  def logs(self, seconds=60):
    try:
      log_dump = broker.coreV1.read_namespaced_pod_log(
        namespace=self.namespace,
        name=self.name,
        since_seconds=seconds
      )
      log_lines = log_dump.split("\n")
      return [res.try_clean_log_line(line) for line in log_lines]
    except ApiException:
      return None

  def shell_exec(self, command):
    return k8s_streaming.stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.name,
      self.namespace,
      command=command,
      stderr=True,
      stdin=False,
      stdout=True,
      tty=False
    )

  def curl_into(self, to_pod, **kwargs):
    kwargs['url'] = to_pod.ip
    return self.run_curl(**kwargs)

  def run_curl(self, **kwargs):
    fmt_command = pod_utils.build_curl_cmd(**kwargs)
    result = self.shell_exec(fmt_command)
    if result is not None:
      result = pod_utils.parse_response(result)
    return result

  def __repr__(self):
    return f"\n{self.ns}:{self.name} | {self.image} | {self.status}"
