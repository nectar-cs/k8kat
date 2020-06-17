from typing import Type

from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.nodes.kat_node import KatNode
from k8_kat.tests.res.base.test_kat_res import Base


class TestKatNode(Base.TestKatRes):

  @classmethod
  def create_res(cls, name, ns=None):
    return cls.first_node()

  @classmethod
  def res_class(cls) -> Type[KatRes]:
    return KatNode

  def tearDown(self) -> None:
    pass

  def get_res(self) -> KatRes:
    return KatNode(self.first_node())

  def test_init(self):
    pass

  def test_find(self):
    self.assertIsNotNone(self.first_node())

  def test_delete_and_wait(self):
    pass

  def test_annotate(self):
    pass

  def test_inflate(self):
    pass

  def test_delete_without_wait(self):
    pass

  @staticmethod
  def first_node():
    return broker.coreV1.list_node().items[0]

