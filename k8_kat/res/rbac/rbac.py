from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes


class KatRole(KatRes):

  @property
  def kind(self):
    return "Role"

  @classmethod
  def _api_methods(cls):
    return(
      dict(
        read=broker.rbacV1.read_namespaced_role,
        delete=broker.rbacV1.delete_namespaced_role,
      )
    )


class KatRoleBinding(KatRes):

  @property
  def kind(self):
    return "RoleBinding"

  @classmethod
  def _api_methods(cls):
    return(
      dict(
        read=broker.rbacV1.read_namespaced_role_binding,
        delete=broker.rbacV1.delete_namespaced_role_binding,
      )
    )


class KatClusterRole(KatRes):

  @property
  def kind(self):
    return "ClusterRole"

  @classmethod
  def is_namespaced(cls):
    return False

  @classmethod
  def _api_methods(cls):
    return(
      dict(
        read=broker.rbacV1.read_cluster_role,
        delete=broker.rbacV1.delete_cluster_role,
      )
    )


class KatClusterRoleBinding(KatRes):

  @property
  def kind(self):
    return "ClusterRoleBinding"

  @classmethod
  def is_namespaced(cls):
    return False

  @classmethod
  def _api_methods(cls):
    return(
      dict(
        read=broker.rbacV1.read_cluster_role_binding,
        delete=broker.rbacV1.delete_cluster_role_binding,
      )
    )
