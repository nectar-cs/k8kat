from urllib.parse import unquote_plus
from http.client import HTTPResponse
from io import BytesIO
from typing import List, Optional, Dict, Callable
from kubernetes.client import V1Container

from k8kat.utils.main import units


class FakeSocket:
  def __init__(self, response_bytes):
    self._file = BytesIO(response_bytes)

  def makefile(self, *args, **kwargs):
    return self._file

def coerce_cmd_format(cmd) -> List[str]:
  if isinstance(cmd, str):
    parts = cmd.split(" ")
    # parts = [part.replace("SPACE_CHAR", " ") for part in parts]
    parts = [unquote_plus(part) for part in parts]
    return parts
  else:
    return cmd

def container_req_or_lim(container: V1Container, metric: str, resource: str) -> Optional[float]:
  """Gets container capacity and returns in cores (cpu) / bytes (memory)."""
  assert metric in ['requests', 'limits']
  assert resource in ['cpu', 'memory', 'ephemeral-storage']
  metrics_dict: Dict = getattr(container.resources, metric, None)
  capacity_expr = (metrics_dict or {}).get(resource, None)
  return capacity_expr and units.parse_quant_expr(capacity_expr)


def build_curl_cmd(**params) -> List[str]:
  raw_headers = params.get('headers', {})
  headers = [f"{0}: {1}".format(k, v) for k, v in raw_headers]
  body = params.get('body', None)

  cmd = [
    "curl" if params.get('with_command') else None,
    "-s",
    "-i",
    '-X', params.get('verb', 'GET'),
    '-H' if headers else None,
    headers if headers else None,
    '-d' if body else None, body if body else None,
    "--connect-timeout", "1",
    f"{params['url']}{params.get('path', '/')}"
  ]
  return [part for part in cmd if part is not None]


def parse_response(response_str) -> Optional[HTTPResponse]:
  if response_str:
    source = FakeSocket(response_str.encode('ascii'))
    # noinspection PyTypeChecker
    response = HTTPResponse(source)
    response.begin()
    return response

  else:
    return None


def when_running_normally(func: Callable) -> Callable:
  """Note: needs to be defined at top of class."""
  def running_normally_func(*args, **kwargs):
    if args[0].is_running_normally():
      return func(*args, **kwargs)
    else:
      return None

  return running_normally_func
