#!/bin/bash

function log() {
  echo "$(date -u --rfc-3339=seconds) - " + "$1"
}

export VAULT_ADDR="https://vault.ci.openshift.org"

vault login -method=oidc

VOLUMES="./volumes"

function dumpSecretToPath() {
    SECRET_PATH=$1
    vault kv get -mount="kv" --format=json "${SECRET_PATH}" > /tmp/secret.json
    KEYS=$(jq .data.data < "/tmp/secret.json" | jq -r keys[])
    SECRET_NAME=$(jq -r '.data.data["secretsync/target-name"]' < "/tmp/secret.json")
    VOLUME_PATH="${VOLUMES}/${SECRET_NAME}"
    mkdir -p "${VOLUME_PATH}"

    for KEY in $KEYS; do
        if [[ "${KEY}" == *"secretsync/target-"* ]]; then
            continue
        fi
        echo "writing secret ${KEY}"
        jq -r --arg key "${KEY}" '.data.data[$key]' < "/tmp/secret.json" > "${VOLUME_PATH}/${KEY}"

    done

    rm /tmp/secret.json
}

SECRETS=(
    "selfservice/vsphere/ibmcloud/ci"
    "selfservice/vsphere/ibmcloud/config"
    "selfservice/vsphere-vmc/ci-route-53"
)

for SECRET in "${SECRETS[@]}"; do
    dumpSecretToPath "${SECRET}"
done

