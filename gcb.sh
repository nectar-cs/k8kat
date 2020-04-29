#!/bin/bash
gcloud builds submit --config cloudbuild.yaml --substitutions=_PASSWORD=foo,_CODECOV_TOKEN=bar
