#!/bin/bash

rm -rf ./vault/home
rm -rf ./artifacts

mkdir -p ./artifacts/profile
mkdir -p ./vault/home/.ssh
mkdir -p ./vault/home/.aws
mkdir -p ./vault/home/.local
mkdir -p ./vault/vsphere

cp ./vault/cluster-profile/* ./artifacts/profile
cp ${HOME}/.ssh/id_rsa.pub ./vault/home/.ssh
cp ${HOME}/.aws/credentials ./vault/home/.aws
cp ${HOME}/.aws/credentials ./vault/vsphere/.awscred
cp ${HOME}/.local/pull-secret.json ./vault/home/.local
