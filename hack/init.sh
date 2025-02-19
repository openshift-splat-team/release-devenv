#!/bin/bash

function cleanup() {
    echo "cleaning up linked files"
    rm .containerfile .collections .env .images Containerfile*

    echo "cleaning up volumes"
    rm -rf volumes
    mkdir volumes
}

function afterLink() {
    echo "intializing artifact volumes"
    ./ci-runner.py --init
}

PLATFORM=$1

case "${PLATFORM}" in
    "vsphere")
        cleanup
        ln -s ./examples/vsphere.collections .collections
        ln -s ./examples/vsphere.images .images
        ln -s ./examples/openshift-e2e-vsphere.env .env
        ln -s ./images/openshift-e2e-vsphere.Containerfile .containerfile
        afterLink
        echo "initialized platform vsphere. this has been tested with the following workflows:"
        echo "- openshift-e2e-vsphere
        "
        echo "further details can be found in docs/examples/openshift-e2e-vsphere.md";;
    "aws-external")
        cleanup
        ln -s ./examples/openshift-e2e-external-aws.env .env
        afterLink
        echo "initialized platform external on aws. this has been tested with the following workflows:"
        echo "- openshift-e2e-external-aws
        "
        echo "further details can be found in docs/examples/openshift-e2e-external-aws.md";;
    *)
        echo "command: ./hack/init.sh <platform>
        "
        echo "initializes ci-runner to run workflows on a specific platform or cluster profile."
        echo "available platforms: vsphere, aws-external"
esac

