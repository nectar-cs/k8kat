from typing import List, Any, Type, Optional
from k8_kat.res.base.kat_res import KatRes
from k8_kat.res.base.label_set_expressions import LabelLogic

class ResQuery:
  def __init__(self, executor, kat: Optional[Type[KatRes]]):
    self._hash = self.default_query_hash()
    self.executor = executor
    self.kat = kat

  def evaluate(self) -> List[KatRes]:
    deps = self.perform_server_eval()
    return self.perform_local_eval(deps)

  def update(self, **kwargs):
    self._hash = {
      **self._hash,
      **kwargs
    }

  def add_feature_filter(self, name, operator, values):
    if name in ['name', 'namespace', 'ns']:
      raise Exception("No using feature_filters for reserved keys!")

    self.feature_filters.append(
      dict(name=name, operator=operator, values=values)
    )

  def reset(self, **kwargs):
    self._hash = {
      **self.default_query_hash(),
      **kwargs
    }

  @property
  def ns_in(self) -> Optional[List[str]]:
    return self._hash['ns_in']

  @property
  def ns_not_in(self):
    return self._hash['ns_nin']

  @property
  def name_in(self):
    return self._hash['name_in']

  @property
  def namespace(self):
    return self._hash['ns_in'][0]

  @property
  def lbs_inc_each(self):
    return self._hash['lbs_inc_each']

  @property
  def lbs_exc_each(self):
    return self._hash['lbs_exc_each']

  @property
  def lbs_inc_any(self):
    return self._hash['lbs_inc_any']

  @property
  def lbs_exc_any(self):
    return self._hash['lbs_exc_any']

  @property
  def feature_filters(self):
    return self._hash['feature_filters']

  def is_single_ns(self) -> bool:
    cond_one = len(self.ns_in or []) == 1
    cond_two = not self.ns_not_in
    return cond_one and cond_two

  def can_be_server_only(self):
    needs_local_label_filtering = self.has_any_lb_any_filters()
    needs_feature_filtering = self.feature_filters
    return not needs_local_label_filtering and not needs_feature_filtering

  def has_any_lb_any_filters(self) -> bool:
    inc_any = self.lbs_inc_any is not None
    exc_any = self.lbs_exc_any is not None
    return inc_any or exc_any

  def gen_server_label_selector(self) -> object:
    if not self.has_any_lb_any_filters():
      return LabelLogic.label_conditions_to_expr(
        self.lbs_inc_each or [],
        self.lbs_exc_each or []
      )
    else:
      return ''

  def perform_server_eval(self) -> List[Any]:
    labels_expr = self.gen_server_label_selector()
    if self.is_single_ns():
      result = self.executor.fetch_for_single_ns(self.namespace, labels_expr)
    else:
      result = self.executor.fetch_for_all_ns(labels_expr)
    return [self.kat(raw_dep) for raw_dep in result]

  def perform_local_eval(self, deps):
    deps = self.executor.filter_ns_in(self.ns_in, deps)
    deps = self.executor.filter_ns_nin(self.ns_not_in, deps)
    deps = self.executor.filter_name_in(self.name_in, deps)

    if self.has_any_lb_any_filters():
      deps = self.executor.filter_lb_inc_any(self.lbs_inc_any, deps)
      deps = self.executor.filter_lb_exc_any(self.lbs_exc_any, deps)
      deps = self.executor.filter_lb_inc_each(self.lbs_inc_each, deps)
      deps = self.executor.filter_lb_exc_each(self.lbs_exc_each, deps)

    for feature_filter in self.feature_filters:
      deps = self.executor.filter_arbitrary_feature(
        feature_filter['name'],
        True if feature_filter['operator'] == 'in' else False,
        feature_filter['values'],
        deps
      )

    return deps

  def delete(self, actual_namespaces, actual_names):
    label_match = self.gen_server_label_selector()
    by_ns_deleter = self.executor.delete_by_label_in_ns
    indiv_deleter = self.executor.delete_individual
    del_by_ns_and_lb = lambda ns: by_ns_deleter(ns, label_match)

    if self.can_be_server_only():
      for namespace in actual_namespaces:
        del_by_ns_and_lb(namespace)
    else:
      for namespace in actual_namespaces:
        for name in actual_names:
          indiv_deleter(namespace, name)

  @staticmethod
  def default_query_hash():
    return {
      'ns_in': None,
      'ns_nin': None,
      'name_in': None,
      'name_nin': None,
      'lbs_inc_each': None,
      'lbs_exc_each': None,
      'lbs_inc_any': None,
      'lbs_exc_any': None,
      'feature_filters': []
    }

  @staticmethod
  def label_query_keys():
    return ['lbs_inc_each', 'lbs_exc_each']
