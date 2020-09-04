from kubernetes.client import V1Role, V1ObjectMeta, V1RoleBinding, V1RoleRef, V1ClusterRole, V1ClusterRoleBinding

from k8kat.auth.kube_broker import broker
from k8kat.res.rbac.rbac import KatRole, KatRoleBinding, KatClusterRole, KatClusterRoleBinding
from k8kat.tests.res.base.test_kat_res import Base


class TestKatRole(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return broker.rbacV1.create_namespaced_role(
      namespace=ns,
      body=V1Role(
        metadata=V1ObjectMeta(name=name),
        rules=[]
      )
    )

  @classmethod
  def res_class(cls):
    return KatRole


class TestKatRoleBinding(Base.TestKatRes):
  def create_res(self, name, ns=None):
    return broker.rbacV1.create_namespaced_role_binding(
      namespace=ns,
      body=V1RoleBinding(
        metadata=V1ObjectMeta(name=name),
        subjects=[],
        role_ref=V1RoleRef(
          kind='Role',
          name='fake',
          api_group='rbac.authorization.k8s.io'
        )
      )
    )

  @classmethod
  def res_class(cls):
    return KatRoleBinding

  def test_annotate(self):
    pass

  def test_list_namespaced_label_filters(self):
    pass

  def test_list_namespaced_field_filters(self):
    pass

class TestKatClusterRole(Base.TestKatRes):
  def create_res(self, name, ns=None):
    return broker.rbacV1.create_cluster_role(
      body=V1ClusterRole(
        metadata=V1ObjectMeta(name=name),
        rules=[]
      )
    )

  @classmethod
  def res_class(cls):
    return KatClusterRole

class TestKatClusterRoleBinding(Base.TestKatRes):
  def create_res(self, name, ns=None):
    return broker.rbacV1.create_cluster_role_binding(
      body=V1ClusterRoleBinding(
        metadata=V1ObjectMeta(name=name),
        subjects=[],
        role_ref=V1RoleRef(
          kind='ClusterRole',
          name='fake',
          api_group='rbac.authorization.k8s.io'
        )
      )
    )

  @classmethod
  def res_class(cls):
    return KatClusterRoleBinding
