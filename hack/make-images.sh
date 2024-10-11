#!/bin/bash

podman build -f .Containerfile -t wip

images=$(jq -c 'keys_unsorted' < .images)

# Remove the brackets and quotes, then convert to a space-separated list
images=$(echo "${images}" | tr -d '[]"')

# pull each image to the local registry and rebuild it to include this repo
for item in ${images//,/ }; do
    name=$(jq -Rn --arg str "${item}" '$str')
    image=$(jq -r -c ".${name}" < .images)
    name="$(jq -rRn --arg str "${item}" '$str')"
    cat > "Containerfile.${name}" <<EOF
FROM "${image}"
WORKDIR /usr/app/src

COPY . .

# Ensure python runner can be bootstrapped
RUN dnf install -y python
RUN python -m ensurepip --default-pip
RUN pip install pyyaml envsubst python-dotenv podman
EOF

    podman build -f "./Containerfile.${name}" -t "${name}"
done