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


def humanize_cpu_quant(millicores: float, with_unit: bool = False) -> str:
  base = "{:.1f}".format(millicores)
  return f"{base} {'Millicores' if with_unit else ''}".strip(' ')


def humanize_mem_quant(byte_value: float) -> str:
  unit_map_items = list(mem_unit_map.items())
  sorted_items = sorted(unit_map_items, key=lambda item: item[1])
  unit, bytes_in_unit = None, None
  for (try_unit, multiplier) in sorted_items:
    bytes_in_unit = byte_value / multiplier
    if try_unit and bytes_in_unit < 1000:
      unit = try_unit
      break
  return f"{int(bytes_in_unit)}{unit}b" if bytes_in_unit else None


mem_unit_map: Dict[str, int] = {
  'Ei' : 2  ** 60,
  'Pi' : 2  ** 50,
  'Ti' : 2  ** 40,
  'Gi' : 2  ** 30,
  'Mi' : 2  ** 20,
  'Ki' : 2  ** 10,
  'm'  : 10 ** -3,
  'mb'  : 10 ** -3,
  'E'  : 10 ** 18,
  'P'  : 10 ** 15,
  'T'  : 10 ** 12,
  'G'  : 10 ** 9,
  'M'  : 10 ** 6,
  'K'  : 10 ** 3,
  ''    : 1
}
