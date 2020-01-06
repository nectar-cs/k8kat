from utils.main.utils import Utils

class PodUtils:

  @staticmethod
  def container_err(cont_status):
    term = Utils.try_or(lambda: cont_status.state.terminated)
    wait = Utils.try_or(lambda: cont_status.state.waiting)
    if term:
      return term.reason
    elif wait:
      return wait.reason
    else:
      return None

  @staticmethod
  def easy_error(state, pod):
    if state == 'Error' or state == 'Failed':
      return PodUtils.container_err(pod)
    else:
      return None

  @staticmethod
  def true_pod_state(given_phase: str, cont_status, give_hard_error: bool):
    error = Utils.try_or(lambda: PodUtils.container_err(cont_status))

    if given_phase == 'Running':
      if not cont_status.ready:
        if not error == 'Completed':
          return (give_hard_error and error) or "Error"
        else:
          return 'Running'
      else:
        return given_phase
    elif given_phase == 'Pending':
      if error == 'ContainerCreating':
        return 'Pending'
      else:
        return 'Error'
    else:
      return given_phase

