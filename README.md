
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/k8kat.svg)](https://pypi.python.org/pypi/k8kat/)
[![PyPI version fury.io](https://badge.fury.io/py/k8kat.svg)](https://pypi.org/project/k8kat/)
[![Client Support Level](https://img.shields.io/badge/kubernetes%20client-alpha-green.svg?style=plastic&colorA=306CE8)](/contributors/design-proposals/api-machinery/csi-new-client-library-procedure.md#client-support-level)
[![codecov](https://codecov.io/gh/nectar-cs/k8kat/branch/master/graph/badge.svg)](https://codecov.io/gh/nectar-cs/k8kat)

## Development

### Environment Setup

During development, use symlinks to include this package instead of pipenv:
cd /project/using/k8kat
ln -s $k8kat_path/k8kat

### Building

https://packaging.python.org/tutorials/packaging-projects/
`python3 setup.py sdist bdist_wheel`
`python3 -m twine upload dist/*`
or 
`twine upload dist/*`

### Cluster Authentication

`broker.connect()`

### Playing Around

`pipenv shell`

`python3 -i shell.py`

### Test Suite
You should be using an empty cluster

Run 

`python3 terraform.py -e=test`

`python3 -i shell.py -e=test`

`python3 -m unittest discover -v`

`python3 -m unittest discover -s tests/k8_kat/base/ -v`

`python3 -m unittest tests/k8_kat/base/test_label_logic.py`