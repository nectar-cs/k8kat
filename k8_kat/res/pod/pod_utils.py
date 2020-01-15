from k8_kat.utils.main import utils


def container_err(cont_status):
  term = utils.try_or(lambda: cont_status.state.terminated)
  wait = utils.try_or(lambda: cont_status.state.waiting)
  if term:
    return term.reason
  elif wait:
    return wait.reason
  else:
    return None

def easy_error(state, pod):
  if state == 'Error' or state == 'Failed':
    return container_err(pod)
  else:
    return None

def true_pod_state(given_phase: str, cont_status, give_hard_error: bool):
  error = utils.try_or(lambda: container_err(cont_status))

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
