from typing import List, Tuple

from k8_kat.res.base.kat_res import KatRes


class ResQueryExec:

  @staticmethod
  def fetch_for_single_ns(ns, label_exp):
    raise Exception("Unimplemented!")

  @staticmethod
  def fetch_for_all_ns(label_exp):
    raise Exception("Unimplemented!")

  @staticmethod
  def delete_by_label_in_ns(ns, label_exp):
    raise Exception("Unimplemented!")

  @staticmethod
  def delete_individual(ns, name):
    raise Exception("Unimplemented!")

  @staticmethod
  def filter_ns_in(ns_names: List[str], resources: List[KatRes]):
    if ns_names is not None:
      return [res for res in resources if res.ns in ns_names]
    else:
      return resources

  @staticmethod
  def filter_ns_nin(ns_names: List[str], resources: List[KatRes]):
    if ns_names is not None:
      return [res for res in resources if res.ns not in ns_names]
    else:
      return resources

  @staticmethod
  def filter_name_in(name_list: List[str], resources: List[KatRes]):
    if name_list is not None:

      return [res for res in resources if res.name in name_list]
    else:
      return resources

  @staticmethod
  def filter_lb_inc_any(label_tups: List[Tuple[str, str]], resources: List[KatRes]):
    if label_tups is not None:
      return [r for r in resources if set(label_tups) & set(r.label_tups)]
    else:
      return resources

  @staticmethod
  def filter_lb_exc_any(label_tups: List[Tuple[str, str]], resources: List[KatRes]):
    if label_tups is not None:
      return [r for r in resources if not set(label_tups) & set(r.label_tups)]
    else:
      return resources

  @staticmethod
  def filter_lb_inc_each(label_tups, resources: List[KatRes]):
    if label_tups is not None:
      return [r for r in resources if set(label_tups).issubset(r.label_tups)]
    else:
      return resources

  @staticmethod
  def filter_lb_exc_each(label_tups, resources: List[KatRes]):
    if label_tups is not None:
      return [r for r in resources if not set(label_tups).issubset(r.label_tups)]
    else:
      return resources

  @staticmethod
  def filter_arbitrary_feature(name, op, values, resources):
    resolve = lambda res: getattr(res, name)
    decide = lambda val: val in values if op else val not in values
    return [r for r in resources if decide(resolve(r))]
