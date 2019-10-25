#!/usr/bin/env python3
from flask import Blueprint, request

from helpers.dep_helper import DepHelper
from helpers.kube_broker import broker
from helpers.pod_helper import PodHelper
from utils.utils import Utils

controller = Blueprint('deployments_controller', __name__)


@controller.route('/api/deployments/across_namespaces')
def across_namespaces():

  def bundle(dep):
    return {
      "name": dep.metadata.name,
      "namespace": dep.metadata.namespace
    }

  broker.check_connected()
  all_deps = broker.appsV1Api.list_deployment_for_all_namespaces().items
  my_deps = [d for d in all_deps if d.metadata.namespace != 'kube-system']
  serialized = [bundle(dep) for dep in my_deps]
  unique_names = set([dep['name'] for dep in serialized])

  output = []

  for name in unique_names:
    matching_deps = list(filter(lambda d: d['name'] == name, serialized))
    corresponding_namespaces = list(map(lambda d: d['namespace'], matching_deps))
    output.append({
      "name": name,
      "namespaces": corresponding_namespaces
    })

  return { "data": output }

@controller.route('/api/deployments/filtered')
def filtered():
  broker.check_connected()
  result = list(map(DepHelper.simple_ser, params_to_deps()))
  return {"data": result}


@controller.route('/api/deployments/<namespace>/<name>')
def show(namespace, name):
  broker.check_connected()
  deployment = DepHelper.find(namespace, name)
  return DepHelper.full_single(deployment)

@controller.route('/api/deployments')
def index():
  broker.check_connected()
  filtered_deployments = params_to_deps()

  if request.args.get('full') == 'true':
    payload = DepHelper.full_list(filtered_deployments)
  else:
    payload = list(map(DepHelper.simple_ser, params_to_deps()))
  return { 'data': payload }

@controller.route('/api/deployments/<namespace>/<name>/pods')
def list_pods(namespace, name):
  deployment = DepHelper.find(namespace, name)
  pods = PodHelper.pods_for_dep(deployment)
  serialized = list(map(PodHelper.full_ser, pods))
  return { 'data': serialized }


def params_to_deps():
  ns_filters = request.args.get('ns_filters', default='').split(',')
  ns_filter_type = request.args.get('ns_filter_type', default='whitelist')

  lb_filters = Utils.parse_dict(request.args.get('lb_filters', default=''))
  lb_filter_type = request.args.get('lb_filter_type', default='blacklist')

  return DepHelper.ns_lb_filter(
    ns_filters,
    ns_filter_type,
    lb_filters,
    lb_filter_type
  )