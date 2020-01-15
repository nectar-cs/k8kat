import re
from typing import Dict

from kubernetes.client import V1Service, V1Pod, V1Deployment

LOG_REGEX = r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b) - - (.*)"

def try_clean_log_line(line):
  try:
    match = re.search(LOG_REGEX, line)
    return match.group(2) or line
  except:
    return line

def dep_owns_pod(dep: V1Deployment, pod: V1Pod) -> bool:
  if dep.metadata.namespace == pod.metadata.namespace:
    dep_matchers = dep.spec.selector.match_labels
    pod_labels = pod.metadata.labels
    if dep_matchers is None or pod_labels is None: return False
    return dep_matchers.items() <= pod_labels.items()
  else:
    return False

def dep_matches_svc(dep: V1Deployment, svc: V1Service) -> bool:
  if dep.metadata.namespace == svc.metadata.namespace:
    dep_pod_labels = dep.spec.template.metadata.labels
    svc_matchers = svc.spec.selector
    if dep_pod_labels is None or svc_matchers is None: return False
    return dep_pod_labels.items() >= svc_matchers.items()
  else:
    return False

def dep_covers_svc_labels(svc: V1Service, labels: Dict[str, str]) -> bool:
  svc_matchers: Dict[str, str] = svc.spec.selector
  return svc_matchers >= labels if svc_matchers is not None else False

def dep_covers_svc_pod(svc: V1Service, pod: V1Pod) -> bool:
  pod_labels: Dict[str, str] = pod.metadata.labels
  svc_matchers: Dict[str, str] = svc.spec.selector
  return svc_matchers >= pod_labels if svc_matchers is not None else False
