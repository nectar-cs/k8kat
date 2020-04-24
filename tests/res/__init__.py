import dotenv

from k8_kat.auth.kube_broker import broker
from k8_kat.utils.main import utils
from k8_kat.utils.testing import test_env

utils.set_run_env('test')
dotenv.load_dotenv()

print("[tests.res.__init__] test_env.apply_perms()")
test_env.apply_perms()
print("[tests.res.__init__] broker.connect()")
broker.connect()
