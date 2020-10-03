from typing import Dict, List, Optional

from typing_extensions import TypedDict

from k8kat.auth.kube_broker import broker
from k8kat.utils.main import utils


class ResDefDict(TypedDict):
  name: str
  shortnames: str
  apigroup: str
  namespaced: str
  kind: str


class ApiDefsMan:
  def __init__(self):
    self._defs_list: Optional[List[ResDefDict]] = None

  def defs_list(self, force_reload=False) -> List[ResDefDict]:
    if force_reload or self._defs_list is None:
      self._defs_list = read_defs_list()
    return self._defs_list

  def find_def(self, kind: str) -> Optional[ResDefDict]:
    predicate = lambda e: res_matches_entry(kind, e)
    return next(filter(predicate, self.defs_list()), None)

  def find_api_group(self, kind: str) -> Optional[str]:
    entry = self.find_def(kind)
    return entry and entry['apigroup']

  def kind2plurname(self, kind):
    entry = self.find_def(kind)
    if entry:
      return entry['name']


def read_defs_list() -> List[ResDefDict]:
  kontext = broker.connect_config.get('context')
  raw = utils.k_exec('api-resources', ctx=kontext)
  return raw_defs2dicts(raw)


def raw_defs2dicts(table_str: str) -> List[ResDefDict]:
  lines = table_str.split("\n")
  headers = list(map(str.lower, split_hard(lines[0])))
  header_positions = positions_in_str(lines[0])
  output = []
  for row in lines[1:]:
    row_cells = []
    for header, start_pos in header_positions.items():
      end_pos = row.find(" ", start_pos)
      end_pos = len(row) if end_pos < 0 else end_pos
      row_cells.append(row[start_pos:end_pos].strip())
    entry = {h: row_cells[i] for (i, h) in enumerate(headers)}
    output.append(entry)
  return output


def res_matches_entry(kind: str, entry: ResDefDict) -> bool:
  if kind == entry.get('kind'):
    return True
  if kind.lower() == entry.get('name'):
    return True
  if f"{kind.lower()}s" == entry.get('name'):
    return True
  return False


def positions_in_str(origin: str) -> Dict[str, int]:
  tokens = split_hard(origin)
  return {token: origin.find(token) for token in tokens}


def split_hard(line: str) -> List[str]:
  return ' '.join(line.split()).split(' ')


api_defs_man = ApiDefsMan()
