import json

import six
from kubernetes.client import ApiClient


def list_namespaced(kind, api_ver, namespace, **kwargs):
  local_var_params = locals()

  all_params = [
    'namespace',
    'field_selector',
    'label_selector',
    'resource_version'
  ]

  for key, val in six.iteritems(local_var_params['kwargs']):
    local_var_params[key] = val

  path_params = {'namespace': local_var_params['namespace']}

  del local_var_params['kwargs']

  query_params = []
  if 'field_selector' in local_var_params:
    query_params.append(('fieldSelector', local_var_params['field_selector']))  # noqa: E501
  if 'label_selector' in local_var_params:
    query_params.append(('labelSelector', local_var_params['label_selector']))  # noqa: E501
  if 'resource_version' in local_var_params:
    query_params.append(('resourceVersion', local_var_params['resource_version']))  # noqa: E501

  header_params = {}

  form_params = []
  local_var_files = {}

  api_client = ApiClient()

  body_params = None
  header_params['Accept'] = api_client.select_header_accept([
    'application/json',
    'application/yaml',
    'application/vnd.kubernetes.protobuf',
    'application/json;stream=watch',
    'application/vnd.kubernetes.protobuf;stream=watch'
  ])

  auth_settings = ['BearerToken']  # noqa: E501

  b0 = f"/api/v1" if api_ver in ['v1', ''] else f'/apis/{api_ver}'
  base = f"{b0}/namespaces/{{namespace}}/{kind}"

  response = api_client.call_api(
    base, 'GET',
    path_params,
    query_params,
    header_params,
    body=body_params,
    post_params=form_params,
    files=local_var_files,
    auth_settings=auth_settings,
    async_req=local_var_params.get('async_req'),
    _return_http_data_only=True,
    _preload_content=False,
    _request_timeout=local_var_params.get('_request_timeout'),
    collection_formats={}
  )

  reg = json.loads(response.data.decode('utf-8'))
  inferred_kind = reg['kind'].replace('List', '')
  for item in reg['items']:
    item['kind'] = inferred_kind
  return reg
