from typing import Callable, TypeVar, List, Dict, Optional, Type

from k8kat.res.base.kat_res import KatRes
from k8kat.res.base.label_set_expressions import label_conditions_to_expr

KT = TypeVar('KT', bound=KatRes)


class Relation(List[KT]):

  def __init__(self, model_class: Type[KT], ns=None, **query):
    if not model_class:
      raise RuntimeError("Cannot compute relation without model_class")

    self.model_class: Type[KT] = model_class
    self.ns: str = ns
    self._query: Dict[str, str] = query

    raw_k8s_res_list = self.perform_in_ns()
    kat_res_list = list(map(model_class, raw_k8s_res_list))
    super().__init__(kat_res_list)

  def perform_in_ns(self):
    impl = self.namespaced_query_impl()
    if self.model_class.is_namespaced():
      return normalize_response(impl(
        namespace=self.ns,
        **self.logical_to_k8s_query()
      ))
    else:
      return normalize_response(impl(
        **self.logical_to_k8s_query()
      ))

  def logical_to_k8s_query(self) -> Dict[str, Optional[str]]:
    k8s_query = dict()
    k8s_query['label_selector'] = process_labels(self._query)
    k8s_query['field_selector'] = process_fields(self._query)
    return k8s_query

  def query(self, **q):
    return Relation(
      self.model_class,
      self.ns,
      **self._query,
      **q
    )

  def namespaced_query_impl(self) -> Callable:
    return self.model_class.k8s_verb_methods()['list']


def process_labels(query) -> Optional[str]:
  with_l, without_l = query.get('labels', {}), query.get('not_labels', {})
  if with_l or without_l:
    return label_conditions_to_expr(with_l.items(), without_l.items())
  else:
    return ''


def process_fields(query) -> Optional[str]:
  with_l, without_l = query.get('fields', {}), query.get('not_fields', {})
  if with_l or without_l:
    return label_conditions_to_expr(with_l.items(), without_l.items())
  else:
    return ''


def normalize_response(result):
  if type(result) == dict:
    return result['items']
  else:
    return result.items
