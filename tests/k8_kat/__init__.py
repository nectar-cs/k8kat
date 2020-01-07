from k8_kat.base.kube_broker import broker
from utils.testing.fixtures import test_env

test_env.terraform()
broker.connect()
