import re
from typing import Optional, Tuple, Dict


def find_multiplier_mapping(expr: str) -> Optional[Tuple[str, int]]:
  for candidate, multiplier in mem_unit_map.items():
    if expr.endswith(candidate):
      return candidate, multiplier
  return None


def quant_expr_to_bytes(expr: str) -> Optional[float]:
  mapping = find_multiplier_mapping(expr)
  if not mapping:
    return None

  try:
    expr_quant_part, multiplier = mapping
    expr_unit_art = float(expr.strip(expr_quant_part))
    return expr_unit_art * multiplier
  except ValueError:
    return None


mem_unit_map: Dict[str, int] = {
  'Ei' : 2  ** 60,
  'EiB' : 2  ** 60,
  'Pi' : 2  ** 50,
  'PiB' : 2  ** 50,
  'Ti' : 2  ** 40,
  'TiB' : 2  ** 40,
  'Gi' : 2  ** 30,
  'GiB' : 2  ** 30,
  'Mi' : 2  ** 20,
  'MiB' : 2  ** 20,
  'Ki' : 2  ** 10,
  'KiB' : 2  ** 10,
  'm'  : 10 ** -3,
  'mb'  : 10 ** -3,
  'E'  : 10 ** 18,
  'EB'  : 10 ** 18,
  'P'  : 10 ** 15,
  'PB'  : 10 ** 15,
  'T'  : 10 ** 12,
  'TB'  : 10 ** 12,
  'G'  : 10 ** 9,
  'GB'  : 10 ** 9,
  'M'  : 10 ** 6,
  'MB'  : 10 ** 6,
  'K'  : 10 ** 3,
  'KB'  : 10 ** 3,
  ''    : 1
}
