from http.client import HTTPResponse
from io import BytesIO
from typing import List, Optional


# noinspection PyUnusedLocal
class FakeSocket:
  def __init__(self, response_bytes):
    self._file = BytesIO(response_bytes)

  def makefile(self, *args, **kwargs):
    return self._file

def coerce_cmd_format(cmd):
  if isinstance(cmd, str):
    return cmd.split(" ")
  else:
    return cmd


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
