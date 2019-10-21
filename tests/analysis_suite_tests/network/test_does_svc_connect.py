import unittest
from tests.analysis_suite_tests.network.base import Base

class TestDoesSvcConnect(Base):

  @classmethod
  def setUpClass(cls):
    super().stdSetUpClass()

  def test_positive(self):
    self.step.perform()
    super().post_test_positive()
    self.assertIsNotNone(self.step.outcomes_bundle['status'])
    self.assertIsNotNone(self.step.outcomes_bundle['raw'])

  def test_negative(self):
    self.step.from_port = self.step.from_port + 1
    self.step.perform()
    super().post_test_negative()

if __name__ == '__main__':
  unittest.main()