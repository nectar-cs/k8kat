
class PodSolver:

  @staticmethod
  def solve(pod):
    events = pod.events()

  @staticmethod
  def is_img_pull_bkf(pod, _):
    return pod.status == 'ImagePullBackOff'

  @staticmethod
  def is_crash_loop_bkf(pod, _):
    return pod.status == 'CrashLoopBackoff'

  @staticmethod
  def is_bad_config_map(pod, events):
    if pod.status == 'RunContainerError':
      suspects = [e for e in events if e.is_config_map_err()]
      return len(suspects) > 0
    return False

  @staticmethod
  def is_bad_secrets(pod, events):
    if pod.status == 'ContainerCreating':
      suspects = [e for e in events if e.is_config_map_err()]
      return len(suspects) > 0
    return False

  @staticmethod
  def is_failing_probe(pod, events):
    if pod.status == 'Running':
      suspects = [e for e in events if e.is_probe_err()]
      return len(suspects) > 0
    return False

  @staticmethod
  def is_insufficient_cpu(pod, events):
    if pod.status == 'Running':
      suspects = [e for e in events if e.is_insufficient_cpu()]
      return len(suspects) > 0
    return False
