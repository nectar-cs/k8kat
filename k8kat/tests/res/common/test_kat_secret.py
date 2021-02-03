import base64
import json

from kubernetes.client import V1Secret, V1ObjectMeta

from k8kat.auth.kube_broker import broker
from k8kat.res.secret.kat_secret import KatSecret
from k8kat.tests.res.base.test_kat_res import Base


class TestKatSecret(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None, **kwargs):
    return broker.coreV1.create_namespaced_secret(
      namespace=ns,
      body=V1Secret(
        metadata=V1ObjectMeta(name=name),
        data=dict(**kwargs)
      )
    )

  def test_decoded_data(self):
    def enc(message: str):
      base64_bytes = base64.b64encode(message.encode('ascii'))
      return base64_bytes.decode('ascii')

    data = {'foo': enc('bar'), 'bar': enc(json.dumps({'x': 'y'}))}

    secret = KatSecret(self.create_res(self.res_name, self.pns, **data))
    contents = secret.decoded_data()
    self.assertEqual('bar', contents['foo'])
    self.assertEqual({'x': 'y'}, json.loads(contents['bar']))

  def test_list_namespaced(self, expected=None):
    pass

  def test_aaa_list_namespaced_filtered(self, expected=None):
    pass

  @classmethod
  def res_class(cls):
    return KatSecret
