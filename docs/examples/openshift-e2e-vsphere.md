# Install a cluster on vSphere

Summary:
- CI workflow: [openshift-e2e-vsphere](https://steps.ci.openshift.org/workflow/openshift-e2e-vsphere)

## Prerequisites

- Project dependencies installed:

```sh
python -m venv ~/.venvs/release-devenv && source ~/.venvs/release-devenv/bin/activate
pip install -r requirements.txt
```

- [release repository](https://github.com/openshift/release) cloned to the path exported by variable `RELEASE_REPO_PATH` (later steps):

```sh
git clone git@github.com:openshift/release ${RELEASE_REPO_PATH}
```

## Setup the workflow

This step guides you to create the environment variable file `.env`.

The `.env` file has all customizations required to execute the workflow.
You can keep as many variants of the workflow you wanted locally, just make sure
it is linked to the `.env` file which is automatically loaded when the `ci-runner.py`
is started.

Option 1) Create an `.env` file based in an example, such as `examples/platform-external.env`:

- Copy the example to `.env`:

```sh
cp examples/platform-external.env .env
```

- Customize to your environment replacing the `<CHANGE_ME>` statements


Option 2) Create your own `.env` file:

- Generate the variables based in template (or copy example .env file `examples/platform-external.env`):

> `AWS_CREDENTIAL_PATH` A custom AWS Credentials file has been created with `[default]` profile pointing to desired AWS account

```sh
cat << EOF > ./.env
# Required by runner
PULL_SECRET_FILE    = '<CHANGE_ME>/.local/pull-secret.json'
RELEASE_REPO_PATH   = '<CHANGE_ME>/code/release'
SSH_PUBLIC_KEY      = '<CHANGE_ME>/.ssh/id_rsa.pub'
AWS_CREDENTIAL_PATH = '<CHANGE_ME>/.aws/credentials-ci'

SKIP_STEPS=ipi-install-rbac,openshift-cluster-bot-rbac

## Required by runner to simulate workflows
CLUSTER_NAME          = '<CHANGE_ME>'
BASE_DOMAIN           = "vmc-ci.devcluster.openshift.com"
LEASED_RESOURCE       = 'vsphere-elastic-1000'
JOB_NAME              = 'periodic-ci-openshift-release-master-nightly-4.16-e2e-vsphere-ovn'
CLUSTER_TYPE          = 'vsphere'
PERSISTENT_MONITORING = 'no'
OCP_ARCH              = 'amd64'

# Override globals
RELEASE_IMAGE                            = 'quay.io/openshift-release-dev/ocp-release:4.16.12-x86_64'
RELEASE_IMAGE_LATEST                     = 'quay.io/openshift-release-dev/ocp-release:4.16.12-x86_64'
OPENSHIFT_INSTALL_RELEASE_IMAGE_OVERRIDE = 'quay.io/openshift-release-dev/ocp-release:4.16.12-x86_64'

# Required by workflow/chain/step
AWS_REGION                    = 'us-west-2'
PROVIDER_NAME                 = 'vsphere'

EOF
```

## Execute the workflow

```sh
./ci-runner.py --init --run-workflow openshift-e2e-vsphere
```

## Additional example: Execute a chain

Alternativelly you can run a chain (group of steps), for example, to install and setup - `pre` steps:

```sh
./ci-runner.py  --run-chain ipi-vsphere-pre
```

## Additional examples: Execute a step

Or eventually execute a specific step using `--run-step`:

```sh
./ci-runner.py  --run-step openshift-e2e-test
```
