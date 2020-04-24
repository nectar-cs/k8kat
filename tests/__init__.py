import dotenv

from k8_kat.utils.main import utils

utils.set_run_env('test')
dotenv.load_dotenv()

print("[tests.__init__] Env force-set to 'test'")
print("[tests.__init__] .env force-reloaded")
