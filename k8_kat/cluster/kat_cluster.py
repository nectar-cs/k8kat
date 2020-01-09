from k8_kat.base.kube_broker import broker


def list_namespaces():
  _namespaces = broker.coreV1.list_namespace().items
  extractor = lambda n: n.metadata.name
  return list(map(extractor, _namespaces))

def label_combinations():
  all_deps = broker.appsV1Api.list_deployment_for_all_namespaces().items
  map_labels_fn = lambda d: d.spec.selector.match_labels
  label_hash_list = list(map(map_labels_fn, all_deps))
  label_list = []

  for _hash in label_hash_list:
    for key in _hash:
      label_list.append(f"{key}:{_hash[key]}")

  return list(set(label_list))
