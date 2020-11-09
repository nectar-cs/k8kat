import json

import six
from kubernetes.client import ApiClient


def svc_proxy_get(name, namespace, path, args, **kwargs):  # noqa: E501
  local_var_params = locals()

  all_params = ['name', 'namespace', 'path', 'path2']  # noqa: E501
  all_params.append('async_req')
  all_params.append('_return_http_data_only')
  all_params.append('_preload_content')
  all_params.append('_request_timeout')

  for key, val in six.iteritems(local_var_params['kwargs']):
    if key not in all_params:
      raise TypeError(
        "Got an unexpected keyword argument '%s'"
        " to method connect_get_namespaced_service_proxy_with_path" % key
      )
    local_var_params[key] = val
  del local_var_params['kwargs']
  # verify the required parameter 'name' is set

  path_params = {
    'name': local_var_params['name'],
    'namespace': local_var_params['namespace'],
    'path': local_var_params['path'],
  }

  query_params = []
  for arg_key, arg_val in list(args.items()):
    query_params.append((arg_key, arg_val))  # noqa: E501

  api_client = ApiClient()

  header_params = {'Accept': api_client.select_header_accept(['*/*'])}

  body_params = None
  # HTTP header `Accept`

  r = api_client.call_api(
    '/api/v1/namespaces/{namespace}/services/{name}/proxy/{path}', 'GET',
    path_params,
    query_params,
    header_params,
    body=body_params,
    post_params=[],
    files={},
    response_type='str',  # noqa: E501
    auth_settings=['BearerToken'],
    async_req=local_var_params.get('async_req'),
    _return_http_data_only=local_var_params.get('_return_http_data_only'),  # noqa: E501
    _preload_content=local_var_params.get('_preload_content', True),
    _request_timeout=local_var_params.get('_request_timeout'),
    collection_formats={})

  return dict(status=r[1], body=r[0].replace("'", "\""))


def list_namespaced_resources(kind, api_group, namespace, **kwargs):
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
  url = f"{request_sig(api_group)}/namespaces/{{namespace}}/{kind}"

  response = api_client.call_api(
    url,
    'GET',
    path_params,
    query_params,
    header_params,
    body=None,
    post_params=[],
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


def delete_namespaced_resource(kind, api_group, namespace, name, **kwargs):
  local_var_params = locals()

  all_params = [
    'namespace',
    'resource_version'
  ]

  for key, val in six.iteritems(local_var_params['kwargs']):
    local_var_params[key] = val

  path_params = {
    'name': local_var_params['name'],
    'namespace': local_var_params['namespace']
  }

  del local_var_params['kwargs']

  query_params = []
  if 'resource_version' in local_var_params:
    query_params.append(('resourceVersion', local_var_params['resource_version']))

  header_params = {}

  api_client = ApiClient()

  body_params = None
  header_params['Accept'] = api_client.select_header_accept([
    'application/json',
    'application/yaml',
    'application/vnd.kubernetes.protobuf',
    'application/json;stream=watch',
    'application/vnd.kubernetes.protobuf;stream=watch'
  ])

  url = f"{request_sig(api_group)}/namespaces/{{namespace}}/{kind}/{{name}}"

  response = api_client.call_api(
    url,
    'DELETE',
    path_params,
    query_params,
    {},
    body=body_params,
    post_params=[],
    files={},
    auth_settings=['BearerToken'],
    async_req=local_var_params.get('async_req'),
    _return_http_data_only=True,
    _preload_content=False,
    _request_timeout=local_var_params.get('_request_timeout'),
    collection_formats={}
  )

  return response.status == 200


def request_sig(api_group: str):
  api_group = '' if api_group == 'v1' else api_group
  prefix = 'api' if api_group == '' else 'apis'
  version = api_group.split('/')[1] if '/' in api_group else 'v1'
  api_group = api_group.split('/')[0] if '/' in api_group else api_group
  parts = [s for s in [prefix, api_group, version] if s]
  return f"/{'/'.join(parts)}"

#
# def http_via_proxy(kind, api_group, namespace, name, path, **kwargs):
#   local_var_params = locals()
#
#   all_params = [
#     'namespace',
#     'resource_version'
#   ]
#
#   for key, val in six.iteritems(local_var_params['kwargs']):
#     local_var_params[key] = val
#
#   path_params = {
#     'name': local_var_params['name'],
#     'namespace': local_var_params['namespace']
#   }
#
#   del local_var_params['kwargs']
#
#   auth_settings = ['BearerToken']  # noqa: E501
#   url = f"{request_sig(api_group)}/namespaces/{{namespace}}/{kind}"
#
#   response = api_client.call_api(
#     url,
#     'GET',
#     path_params,
#     query_params,
#     header_params,
#     body=body_params,
#     post_params=form_params,
#     files=[],
#     auth_settings=auth_settings,
#     async_req=local_var_params.get('async_req'),
#     _return_http_data_only=True,
#     _preload_content=False,
#     _request_timeout=local_var_params.get('_request_timeout'),
#     collection_formats={}
#   )
#
#   return response.data.decode('utf-8'))
