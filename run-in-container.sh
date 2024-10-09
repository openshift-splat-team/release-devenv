#!/bin/bash

. pre.sh

podman build -f Containerfile -t ci-runner

podman run -v $(pwd)/vault:/var/run/vault:z \
  -v $(pwd)/vault/vsphere-ibmcloud-ci:/var/run/vsphere-ibmcloud-ci:z \
  -v $(pwd)/artifacts:/artifacts:z \
  -v $(pwd)/../release:/var/run/vault/home/code/release:z \
  -v $(pwd)/vault/cluster-profile:/var/run/secrets/ci.openshift.io/cluster-profile:z \
  ci-runner:latest ./ci-runner.py $@