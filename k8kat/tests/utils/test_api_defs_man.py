import unittest

from k8kat.auth.kube_broker import broker
from k8kat.tests.res.base.cluster_test import ClusterTest

from k8kat.utils.main.api_defs_man import raw_defs2dicts, read_defs_list, api_defs_man


class TestApisDefsMan(ClusterTest):
  def test_raw_defs2dict(self):
    with open('mock_api_defs.txt') as file:
      raw_defs = file.read()
    actual = raw_defs2dicts(raw_defs)

    self.assertEqual(2, len(actual))

    self.assertEqual('configmaps', actual[0]['name'])
    self.assertEqual('', actual[0]['apigroup'])

    self.assertEqual('deployments', actual[1]['name'])
    self.assertEqual('apps', actual[1]['apigroup'])

  def test_read_defs_list(self):
    if broker.is_in_cluster_auth():
      read_defs_list()

  def test_kind2plurname(self):
    self.assertEqual('pods', api_defs_man.kind2plurname('Pod'))
    self.assertEqual('pods', api_defs_man.kind2plurname('pod'))
    self.assertEqual('pods', api_defs_man.kind2plurname('pods'))
    self.assertEqual('pods', api_defs_man.kind2plurname('Pods'))

  def test_find_api_group(self):
    api_defs_man._defs_list = [
      {'name': 'foos', 'apigroup': 'g1', 'kind': 'NotFoo'},
      {'name': 'bars', 'apigroup': 'g2', 'kind': 'NotBar'},
      {'name': 'cars', 'apigroup': 'g3', 'kind': 'Car'}
    ]
    self.assertEqual('g1', api_defs_man.find_api_group('foos'))
    self.assertEqual('g2', api_defs_man.find_api_group('bar'))
    self.assertEqual('g3', api_defs_man.find_api_group('Car'))
