from k8_kat.res.base.k8_kat import K8Kat


class DepWarnings:

  @staticmethod
  def check_pod_template_inclusive(dep):
    template, sel_labels = dep.template_labels, dep.pod_select_labels
    return template.items() >= sel_labels.items()

  @staticmethod
  def check_no_pods_eavesdrop(dep):
    template = dep.template_labels.items()
    other_ns_deps = K8Kat.deps().ns(dep.ns).not_names(dep.name)
    drops = lambda o_dep: dep.pod_select_labels.items() <= template
    eavesdroppers = [d for d in other_ns_deps if drops(d)]
    return len(eavesdroppers) == 0

  @staticmethod
  def check_labels_unique(dep):
    twins = K8Kat.deps().ns(dep.ns).lbs_inc_each(dep.labels)
    return len(twins.go()) == 0

  @staticmethod
  def check_no_selector_spill(dep):
    pass

  @staticmethod
  def check_pods_in_same_ns(dep):
    pods_ns = dep.raw.spec.template.metadata.namespace
    return dep.ns == pods_ns
