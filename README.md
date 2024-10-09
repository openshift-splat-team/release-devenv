# Overview

Verifying the functionality of PRs in the `release` repo can be a bit challenging due to the large number of steps and/or jobs that are run when a PR is tested. The intent of this project is to provide a development environment where changes to the `release` repo can be verified locally while still working with real cloud backends.  This environment is not intended to replace verifying a PR via `pj-rehearse`. 

This tool requires in-depth knowledge of how the CI workflow you're working with works. You'll need to provide the necessary environment variables and make updates to accomodate any 
other artifacts the workflow may need. Additionally, if any tools are required by the workflow that are not provisioned in the workflow, those tools must be made available on the system path.

## Requirements

- Necessary credentials to install in your cloud or enviornment of choice

## Using the tool

Each workflow may require slightly different artifacts and environment variables. To accomodate this, each platform has a platform-specific `env.py`. This file should be in the same directory as
`main.py` when running the tool. `env.py` can be symlinked to the same directory as `main.py`.

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
  --intialize           Initializes local directories to prepare for running artifacts
```

When adding support for a new workflow, the process is somewhat trial and error to determine which variables need to be defined. 

## Shared Directory

Artifacts from the workflow and the shared_dir are located in `/tmp`. The `--initialize` flag initializes the shared and artifact directories
in preparation to run a workflow.

# Platforms

Platforms and associated variants are stored in `./platforms`. Each platform variant will have the following files:
- `env.py` - defines environment variables used by the job
- `pre.sh` - handles initialization steps required before the workflow runs
- `Containerfile` - defines a container image which packages required tools 
- `init.sh` - creates sym-links to files required to setup and run the workflow on specific platform

# Running in a Container

## Initializing a Platform

Before the container can be used to run a workflow, the platform must be initialized. From the root of the repository, run the `init.sh`
For example, for vSphere:

`./platforms/vsphere/init.sh`

This symlinks files to the root of the repository which are used by the ci-runner.

## Initializing Secrets

Secrets are stored under `./vault` in the root of the repository. `./vault` is mounted to `/var/run/vault` in the container.

## Running

To prevent running a workflow from running tools which may only be present on the host and/or from installing tools which could impact the host, 
`./run-in-container.sh` will create a container which mounts directories on the host. The following directories are created:

- `./artifacts` -- contains artifacts from the workflow
- `./vault` -- contains secrets from vault. the paths of the secrets should match what steps expect.
- `./vault/home` -- the home dir used during the job. artifacts such as public key, pull-secret, etc.. are staged here for use by the workflow
- `./platforms` -- contains the platforms supported by `ci-runner`

`./run-in-container.sh` accepts the same arguments as `ci-runner.py`.

__Note:__ Do not commit anything under `vault` or `artifacts`. 

