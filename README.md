
## Development

### Environment Setup

### Cluster Authentication

`broker.connect()`

### Playing Around

`python3 -i shell.py`

### Test Suite
You should be using an empty cluster
`python3 -i shell.py -e=test`
`python3 -m unittest discover -s tests/k8_kat/base/ -v`
`python3 -m unittest tests/k8_kat/base/test_label_logic.py`