import json

from kubernetes.client import V1ConfigMap, V1ObjectMeta

def json_map(name, ns, master_key, dict_value):
  return V1ConfigMap(
    metadata=V1ObjectMeta(
      name=name,
      namespace=ns
    ),
    data={master_key: json.dumps(dict_value)}
  )
