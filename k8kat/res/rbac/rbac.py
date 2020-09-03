from typing import List

from kubernetes.client import V1Role, V1PolicyRule

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes
from k8kat.utils.main.class_property import classproperty

main_verbs = ['list', 'read', 'patch', 'create', 'delete']


def verbs_to_bools(rule_verbs: List[str]):
  if rule_verbs == ['*']:
    return {verb: True for verb in main_verbs}
  else:
    return {verb: (verb in rule_verbs) for verb in main_verbs}


class KatRole(KatRes):

  @classproperty
  def kind(self):
    return "Role"

  def body(self) -> V1Role:
    return self.raw

  def matrix_form(self):
    out = []
    for rule in self.body().rules:
      for resource_type in rule.resources:
        out.append(dict(
          resource=resource_type,
          apis=rule.api_groups,
          verbs=verbs_to_bools(rule.verbs)
        ))
    return out

  @classmethod
  def k8s_verb_methods(cls):
    return(
      dict(
        read=broker.rbacV1.read_namespaced_role,
        patch=broker.rbacV1.patch_namespaced_role,
        delete=broker.rbacV1.delete_namespaced_role,
        list=broker.rbacV1.list_namespaced_role,
      )
    )


class KatRoleBinding(KatRes):

  @classproperty
  def kind(self):
    return "RoleBinding"

  @classmethod
  def k8s_verb_methods(cls):
    return(
      dict(
        read=broker.rbacV1.read_namespaced_role_binding,
        patch=broker.rbacV1.patch_namespaced_role_binding,
        delete=broker.rbacV1.delete_namespaced_role_binding,
        list=broker.rbacV1.list_namespaced_role_binding
      )
    )


class KatClusterRole(KatRes):

  @classproperty
  def kind(self):
    return "ClusterRole"

  @classmethod
  def is_namespaced(cls):
    return False

  @classmethod
  def k8s_verb_methods(cls):
    return(
      dict(
        read=broker.rbacV1.read_cluster_role,
        patch=broker.rbacV1.patch_cluster_role,
        delete=broker.rbacV1.delete_cluster_role,
      )
    )


class KatClusterRoleBinding(KatRes):

  @classproperty
  def kind(self):
    return "ClusterRoleBinding"

  @classmethod
  def is_namespaced(cls):
    return False

  @classmethod
  def k8s_verb_methods(cls):
    return(
      dict(
        read=broker.rbacV1.read_cluster_role_binding,
        patch=broker.rbacV1.patch_cluster_role_binding,
        delete=broker.rbacV1.delete_cluster_role_binding,
      )
    )
