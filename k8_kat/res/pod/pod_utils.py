import re

from k8_kat.utils.main import utils

HEADER_BODY_DELIM = "\r\n\r\n"

def build_curl_cmd(**params):
  raw_headers = params.get('headers', {})
  headers = [f"{0}: {1}".format(k, v) for k, v in raw_headers]
  body = params.get('body', None)

  cmd = [
    "curl",
    "-s",
    "-i",
    '-X', params.get('verb', 'GET'),
    '-H', headers,
    '-d' if body else None, body if body else None,
    "--connect-timeout", "1",
    f"{params['url']}{params.get('path', '/')}"
  ]
  return [part for part in cmd if part is not None]

def parse_status(header):
  out = re.search('HTTP/(\d*)\.(\d*) (\d*) .*', header)
  return out.group(3)

def format_empty_response():
  return {
    "raw": "N/A",
    "headers": ["N/A"],
    "body": "Could not connect",
    "status": "N/A",
    "finished": False
  }

def parse_response(response):
  if response:
    parts = response.split(HEADER_BODY_DELIM)
    headers = parts[0].split("\r\n")
    body_parts = parts[1:len(parts)]
    body = body_parts[0]

    return {
      "raw": response,
      "headers": headers,
      "body": body,
      "status": parse_status(headers[0]),
      "finished": True
    }
  else:
    return format_empty_response()


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
