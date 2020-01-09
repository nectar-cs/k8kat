from k8_kat.utils.main.res_utils import ResUtils


class RsOutbound:

  @staticmethod
  def rs_dep(rs):
    refs = rs.metadata.owner_references
    rs_refs = [ref for ref in refs if ref.kind == 'Deployment']
    if len(rs_refs) is 1:
      rs_name = rs_refs[0].name
      return ResUtils.find_dp(rs.metadata.namespace, rs_name)
    else:
      return None
