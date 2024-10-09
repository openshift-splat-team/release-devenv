#!/bin/bash

. pre.sh

podman build -f Containerfile -t ci-runner

podman run -v $(pwd)/vault:/var/run/vault:z \
  -v $(pwd)/artifacts:/artifacts:z \
  -v $(pwd)/../release:/var/run/vault/home/code/release:z \
  ci-runner:latest ./ci-runner.py $@