from typing import Optional, Tuple, Dict, Union


def find_multiplier_mapping(expr: str) -> Optional[Tuple[str, Union[int,float]]]:
  """Finds the correct multiplier for unit conversion."""
  if expr is None:
    return None
  for candidate, multiplier in unit_map.items():
    if expr.endswith(candidate):
      return candidate, multiplier
  return None

def parse_quant_expr(src_expr: str, target: str = '') -> Optional[float]:
  """Parses the source expression into standard units
  or target units (if specified)."""
  if src_expr is not None:
    src_mapping = find_multiplier_mapping(src_expr)
    target_mapping = find_multiplier_mapping(target)
    if not src_mapping or not target_mapping:
      return None

    try:
      src_quantity, src_multiplier = src_mapping
      _, target_multiplier = target_mapping
      unitless = float(src_expr.strip(src_quantity))
      return unitless * src_multiplier / target_multiplier
    except ValueError:
      return None
  else:
    return None

def humanize_cpu_quant(cores: float, with_unit: bool = False) -> str:
  """Returns CPU quantity in cores rounded to single decimal."""
  base = "{:.1f}".format(cores)
  return f"{base} {'Cores' if with_unit else ''}".strip(' ')


def humanize_mem_quant(byte_value: float) -> Optional[str]:
  """ Returns memory quantity converted from bytes to higher level units.
  Automatically picks the right units for friendliest display."""
  unit_map_items = list(unit_map.items())
  sorted_items = sorted(unit_map_items, key=lambda item: item[1])
  unit, bytes_in_unit = None, None
  for (try_unit, multiplier) in sorted_items:
    bytes_in_unit = byte_value / multiplier
    if try_unit and bytes_in_unit < 1000:
      unit = try_unit
      break
  return f"{int(bytes_in_unit)}{unit}b" if bytes_in_unit else None


unit_map: Dict[str, Union[int, float]] = {
  'Ei'   : 2  ** 60,
  'Pi'   : 2  ** 50,
  'Ti'   : 2  ** 40,
  'Gi'   : 2  ** 30,
  'Mi'   : 2  ** 20,
  'Ki'   : 2  ** 10,
  'E'    : 10 ** 18,
  'P'    : 10 ** 15,
  'T'    : 10 ** 12,
  'G'    : 10 ** 9,
  'M'    : 10 ** 6,
  'K'    : 10 ** 3,
  'k'    : 10 ** 3,  # k8s uses both K and k for "kilo"
  'm'    : 10 ** -3,
  'micro': 10 ** -6,
  'n'    : 10 ** -9,
  'p'    : 10 ** -12,
  ''     : 1
}