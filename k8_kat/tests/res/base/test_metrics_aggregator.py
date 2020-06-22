import unittest


class Base:
  class MetricsAggregator(unittest.TestCase):

    def test_fetch_usage(self):
      res = self.res_class()(self.create_res(self.res_name, self.pns))
      with patch(f"{self.res_class().__module__}.{self.res_class().__name__}.load_metrics") as mocked_metrics:
        mocked_metrics.return_value = [dict(containers=[
          {'name': 'pod_name', 'usage': {'cpu': '3910299n', 'memory': '17604Ki'}}])]

        self.assertEqual(res.resource_usage('cpu'),
                         round(units.parse_quant_expr('3910299n'), 3))
        self.assertEqual(res.resource_usage('memory'),
                         round(units.parse_quant_expr('17604Ki'), 3))

        self.assertEqual(mocked_metrics.call_count, 2)

    def test_fetch_usage_with_undefined(self):
      res = self.res_class()(self.create_res(self.res_name, self.pns))
      with patch(
        f"{self.res_class().__module__}.{self.res_class().__name__}.load_metrics") as mocked_metrics:
        mocked_metrics.return_value = None

        self.assertEqual(res.resource_usage('cpu'), None)
        self.assertEqual(res.resource_usage('memory'), None)

        self.assertEqual(mocked_metrics.call_count, 2)
