#!/bin/bash

if [[ "$1" == "test" ]]; then
  pipenv run python3 -m unittest
  echo $CODECOV_TOKEN
  bash <(curl -s https://codecov.io/bash); exit 0
elif [[ "$1" == "publish" ]]; then
  pipenv run python3 setup.py sdist bdist_wheel
  pipenv run python3 -m twine upload -u xnectar -p "$PASSWORD" dist/*; exit 0
else
  echo "Arg 1 must be 'test' or 'publish', was '$1'"
fi