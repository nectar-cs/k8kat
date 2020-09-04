from kubernetes.client import V1PersistentVolumeClaim, V1ObjectMeta, V1PersistentVolumeClaimSpec, V1ResourceRequirements

from k8kat.auth.kube_broker import broker
from k8kat.res.pvc.kat_pvc import KatPvc
from k8kat.tests.res.base.test_kat_res import Base


class TestKatPvc(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return broker.coreV1.create_namespaced_persistent_volume_claim (
      namespace=ns,
      body=V1PersistentVolumeClaim(
        metadata=V1ObjectMeta(
          name=name,
          finalizers=[]
        ),
        spec=V1PersistentVolumeClaimSpec(
          access_modes=['ReadWriteOnce'],
          resources=V1ResourceRequirements(
            requests=dict(storage='100Mi')
          )
        )
      )
    )

  def test_annotate(self):
    pass

  def test_list_namespaced_label_filters(self):
    pass

  def test_list_namespaced_field_filters(self):
    pass

  @classmethod
  def res_class(cls):
    return KatPvc
