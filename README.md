# Overview

Verifying the functionality of PRs in the `release` repo can be a bit challenging due to the large number of steps and/or jobs that are run when a PR is tested. The intent of this project is to provide a development environment where changes to the `release` repo can be verified locally while still working with real cloud backends.  This environment is not intended to replace verifying a PR via `pj-rehearse`. 

This tool requires in-depth knowledge of how the CI workflow you're working with works. You'll need to provide the necessary environment variables and make updates to accomodate any other artifacts the workflow may need. Additionally, if any tools are required by the workflow that are not provisioned in the workflow, those tools must be made available in the container image associated with the individual steps.

## Requirements

- Necessary credentials to install in your cloud or enviornment of choice
- A firm understanding of the release repo and prow artifacts
- Podman

## Running the Tool

### Setting up Images

Prow steps are run on specific images. The image used in a prow step is defined in the `from:` attribute:

```yaml
ref:
  as: ipi-conf-vsphere
  from: tools <---
  commands: ipi-conf-vsphere-commands.sh
  resources:
    requests:
```

In the `examples` directory, there are `.images` files for each platform. The images file is a JSON file which 
defines a mapping of image names to image pull specs:

```json
{
    "tools": "quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:7322ae0a4a9b0d8550ac92435010461ed4bedf0b59b03b83bf85bfb34c2de2f8",
    "cli": "quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:8255266c07d4dec7290e48b35b53f7aacb20bc6b642ee096b3bf31df83562af5",
    "installer": "localhost/dev:latest",
    "upi-installer": "localhost/dev:latest",
    "test": "quay.io/openshift-release-dev/ocp-v4.0-art-dev@sha256:472c37c2eec3a84d570316f57ec323efaf32b23a43156bb81f8bd244be734662",
    "nested-environment-builder": "localhost/dev:latest"
}
```

If an image mapping isn't found, `localhost/dev:latest` will be used. `localhost/dev:latest` is a container image that is built from this project. The Containerfile for the image is located in the `images` directory. This image can be useful for quickly prototyping changes necessary in an image to run a given step.

#### Building Local Images

All images are built and tagged locally. `ci-runner` requires a few dependencies which are add to each image while they are being built and tagged locally.
To build images, run: `./hack/build-local-images.sh`.

### Volumes

Volumes are located in the `volumes` directory. Secrets, job artifacts, shared_dir, and logs are all kept in `volumes`. 

#### Secrets

Secrets are stored in sub-directories. Each sub-directory contains the same file names and structure as the associated vault secrets. Secrets are referred to as 
`credentials` in the step yaml:

```yaml
  credentials:
  - namespace: test-credentials
    name: vsphere-vmc
    mount_path: /var/run/vault/vsphere
  - namespace: test-credentials
    name: vsphere-ibmcloud-config
    mount_path: /var/run/vault/vsphere-ibmcloud-config
  - namespace: test-credentials
    name: ci-ibmcloud
    mount_path: /var/run/vault/ibmcloud
```
Each credential will require a folder of the same name in `volumes`. If a secret isn't found locally, the step will proceed with a warning.

#### Syncing Vault

Secrets can be synced from a Vault instance to `volumes`. In `examples`, there is a definition of required collections in `.collections` files.


#### Artifacts

#### Shared Dir




## Running the Tool Locally

__NOTE:__ Use this with care! It is recommended that image based execution be used to reduce the chance of changes being made to the host environment.

Each workflow may require slightly different artifacts and environment variables. To accomodate this, each platform has a platform-specific `env.py`. This file should be in the same directory as `main.py` when running the tool. `env.py` can be symlinked to the same directory as `main.py`.

`ci-runner.py` allows for a workflow, chain, or individual step to be run. 

```sh
$ ./ci-runner.py --help
usage: ci-runner.py [-h] [--run-chain RUN_CHAIN] [--run-step RUN_STEP] [--run-workflow RUN_WORKFLOW] [--intialize]

A CLI tool for executing CI operator artifacts

options:
  -h, --help            show this help message and exit
  --run-chain RUN_CHAIN
                        Run the specified chain
  --run-step RUN_STEP   Run the specified step
  --run-workflow RUN_WORKFLOW
                        Run the specified workflow
  --init                Initializes local directories to prepare for running artifacts
```

When adding support for a new workflow, the process is somewhat trial and error to determine which variables need to be defined. 

## Shared Directory

Artifacts from the workflow and the shared_dir are located in `/tmp`. The `--initialize` flag initializes the shared and artifact directories
in preparation to run a workflow.


## Examples

Additionally, you can explore the additional example documentation
at [`docs/examples`](./docs/examples), as well example environment
files hosted under [`examples`](./examples) directory.
