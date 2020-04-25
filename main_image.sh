#!/bin/bash

if [[ "$1" == "test" ]]; then
  pipenv run python3 -m unittest
elif [[ "$1" == "publish" ]]; then
  pipenv run python3 setup.py sdist bdist_wheel
  pipenv run python3 -m twine upload -u xnectar -p "$PASSWORD" dist/*
else
  echo "Arg 1 must be 'test' or 'publish', was '$1'"
fi