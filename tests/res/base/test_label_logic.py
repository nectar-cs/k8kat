import unittest
from typing import Tuple

from k8_kat.res.base.label_set_expressions import LabelLogic

kls = LabelLogic

class TestLabelLogic(unittest.TestCase):

  @property
  def and_tuple(self) -> Tuple:
    return 'app', 'backend'

  @property
  def baked_or_tuple(self) -> Tuple:
    return 'app', ['backend', 'kapi']

  def test_and_to_exp(self):
    self.assertEqual(kls.and_to_exp(self.and_tuple, True), 'app=backend')
    self.assertEqual(kls.and_to_exp(self.and_tuple, False), 'app!=backend')

  def test_or_set_to_exp(self):
    result = kls.or_set_to_exp(self.baked_or_tuple, True)
    self.assertEqual(result, 'app in (backend, kapi)')

    result = kls.or_set_to_exp(self.baked_or_tuple, False)
    self.assertEqual(result, 'app notin (backend, kapi)')

  def test_ands_to_exps(self):
    r1 = kls.ands_to_exps([], True)
    r2 = kls.ands_to_exps([self.and_tuple], True)
    r3 = kls.ands_to_exps([self.and_tuple, self.and_tuple], False)

    self.assertEqual(r1, [])
    self.assertEqual(r2, ['app=backend'])
    self.assertEqual(r3, ['app!=backend', 'app!=backend'])

  def test_ors_to_exp(self):
    r1 = kls.ors_to_exp([], True)
    r2 = kls.ors_to_exp([('app', 'one')],  True)
    r3 = kls.ors_to_exp([('app', 'one'), ('type', 'two')], True)
    r4 = kls.ors_to_exp([('app', 'one'), ('app', 'two')], True)
    r5 = kls.ors_to_exp([('app', 'one'), ('app', 'two'), ('type', 'three')], True)

    self.assertCountEqual(r1, [])
    self.assertCountEqual(r2, ['app in (one)'])
    self.assertCountEqual(r3, ['app in (one)', 'type in (two)'])
    self.assertCountEqual(r4, ['app in (one, two)'])
    self.assertCountEqual(r5, ['app in (one, two)', 'type in (three)'])

  def test_partition_tups(self):
    self.assertSequenceEqual(kls.partition_tups([]), [[], []])

    tups = [('app', 'one'), ('region', 'us')]
    self.assertSequenceEqual(kls.partition_tups(tups), [tups, []])

    tups = [('app', 'one'), ('app', 'two'), ('region', 'us')]
    expect = [[('region', 'us')], [('app', 'one'), ('app', 'two')]]
    actual = kls.partition_tups(tups)
    self.assertSequenceEqual(actual, expect)

  def test_assemble_expr_lists(self):
    r1 = kls.assemble_expr_lists([])
    r2 = kls.assemble_expr_lists([[]])
    r3 = kls.assemble_expr_lists([['app=backend']])
    r4 = kls.assemble_expr_lists([['app=kapi'], ['app=backend'], []])
    r5 = kls.assemble_expr_lists([['app!=backend'], ['app in (one)']])

    self.assertEqual(r1, '')
    self.assertEqual(r2, '')
    self.assertEqual(r3, 'app=backend')
    self.assertEqual(r4, 'app=kapi,app=backend')
    self.assertEqual(r5, 'app!=backend,app in (one)')

  def test_integration(self):
    r = kls.label_conditions_to_expr(
      [('debug', 'true'), ('market', 'asia')],
      [],
    )
    self.assertEqual(r, 'debug=true,market=asia')

    r2 = kls.label_conditions_to_expr(
      [('debug', 'true'), ('market', 'asia'), ('market', 'eu')],
      []
    )
    self.assertEqual(r2, 'debug=true,market in (asia, eu)')

    r3 = kls.label_conditions_to_expr(
      [('app', 'admin')],
      [('kind', 'static'), ('kind', 'electric')]
    )
    self.assertEqual(r3, 'app=admin,kind notin (static, electric)')


if __name__ == '__main__':
    unittest.main()
