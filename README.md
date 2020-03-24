
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