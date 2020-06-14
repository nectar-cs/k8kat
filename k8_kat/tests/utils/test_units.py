import unittest

from k8_kat.utils.main import units


class TestUnits(unittest.TestCase):

  def test_valid_cpu_expr_to_millicores(self):
    self.assertEqual(1.5, units.quant_expr_to_bytes("1.5"))
    self.assertEqual(1.5, units.quant_expr_to_bytes("15e2m"))
    self.assertEqual(1.5, units.quant_expr_to_bytes("1500m"))

  def test_valid_mem_expr_to_bytes(self):
    self.assertEqual(128974848, units.quant_expr_to_bytes("123Mi"))
    self.assertEqual(129000000, units.quant_expr_to_bytes("129M"))
    self.assertEqual(1, units.quant_expr_to_bytes("1e3m"))
    self.assertEqual(129000000, units.quant_expr_to_bytes("129e6"))
    self.assertEqual(1000, units.quant_expr_to_bytes("1000.0"))

  def test_invalid_expr_to_bytes(self):
    self.assertEqual(None, units.quant_expr_to_bytes("123MI"))
    self.assertEqual(None, units.quant_expr_to_bytes(""))
    self.assertEqual(None, units.quant_expr_to_bytes("str"))
