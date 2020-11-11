from kubernetes.client import V1Event

from k8kat.utils.main.types import IntelDict


class KatEvent:

  def __init__(self, raw):
    self.raw = raw

  def body(self) -> V1Event:
    return self.raw

  def intel_bundle(self) -> IntelDict:
    return dict(
      type='Event',
      message=self.message,
      status=self.reason
    )

  @property
  def name(self):
    return self.raw.metadata.name

  @property
  def namespace(self):
    return self.raw.metadata.namespace

  @property
  def for_uid(self):
    return self.raw.involved_object.uid

  @property
  def for_kind(self):
    return self.raw.involved_object.kind

  @property
  def for_ns(self):
    return self.raw.involved_object.namespace

  @property
  def for_name(self):
    return self.raw.involved_object.name

  @property
  def reason(self):
    return self.raw.reason

  @property
  def message(self):
    return self.raw.message

  @property
  def severity(self):
    return self.raw.type

  @property
  def occurred_at(self):
    return self.raw.first_timestamp

  def is_failure(self) -> bool:
    return not self.body().type == 'Normal'

  def hint(self):
    if self.is_config_map_err():
      return "This suggests it's not reading a ConfigMap right."
    elif self.is_secrets_err():
      return "This suggests it's not reading a Secret right."
    elif self.is_probe_err():
      return "This suggests your liveness probe is failing."
    elif self.is_insufficient_cpu():
      return "This suggests your pod may be CPU starved."
    elif self.is_app_crashing():
      return "This suggests the app inside the container keeps crashing at launch."

  def is_for(self, kat_res):
    return self.for_uid == kat_res.uid

  def is_config_map_err(self):
    return "configmaps" in self.message

  def is_secrets_err(self):
    return "with: secrets" in self.message

  def is_probe_err(self):
    return self.reason == 'Unhealthy'

  def is_app_crashing(self):
    return "Back-off restarting" in self.message

  def is_insufficient_cpu(self):
    return "Insufficient cpu" in self.message
