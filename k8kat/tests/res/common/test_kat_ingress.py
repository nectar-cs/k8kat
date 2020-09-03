from typing import Type

from kubernetes.client import ExtensionsV1beta1Ingress, V1ObjectMeta, ExtensionsV1beta1IngressSpec, \
  ExtensionsV1beta1IngressRule, ExtensionsV1beta1HTTPIngressPath, ExtensionsV1beta1IngressBackend, \
  ExtensionsV1beta1HTTPIngressRuleValue

from k8kat.auth.kube_broker import broker
from k8kat.res.base.kat_res import KatRes
from k8kat.res.ingress.kat_ingress import KatIngress
from k8kat.tests.res.base.test_kat_res import Base


class TestKatIngress(Base.TestKatRes):


  @classmethod
  def create_res(cls, name, ns=None):
    return create(name=name, ns=ns)

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatIngress

  def test_basic_rules(self):
    ing = KatIngress(create(
      ns=self.pns,
      name=self.res_name,
      host='h1',
      svc='s1',
      port='p1',
      path='/p'
    ))
    result = ing.basic_rules()
    self.assertEqual({
      'h1': [
        dict(
          service='s1',
          port='p1',
          path='/p'
        )
      ]
    }, result)


def create(**kwargs):
  return broker.extsV1.create_namespaced_ingress(
    namespace=kwargs['ns'],
    body=ExtensionsV1beta1Ingress(
      metadata=V1ObjectMeta(
        name=kwargs['name'],
      ),
      spec=ExtensionsV1beta1IngressSpec(
        rules=[
          ExtensionsV1beta1IngressRule(
            host=kwargs.get('host', 'foo.bar'),
            http=ExtensionsV1beta1HTTPIngressRuleValue(
              paths=[
                ExtensionsV1beta1HTTPIngressPath(
                  path=kwargs.get('path', '/foo'),
                  backend=ExtensionsV1beta1IngressBackend(
                    service_name=kwargs.get('svc', 'svc'),
                    service_port=kwargs.get('port', 80)
                  )
                )
              ]
            )
          )
        ]
      )
    )
  )
