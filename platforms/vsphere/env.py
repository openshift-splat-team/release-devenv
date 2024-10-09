import os

CLUSTER_NAME        = 'rvanderp-external'
HOME_DIR            = '/var/run/vault/home'
RELEASE_IMAGE       = 'quay.io/openshift-release-dev/ocp-release:4.16.12-x86_64'
SSH_PUBLIC_KEY      = f'{HOME_DIR}/.ssh/id_rsa.pub'
AWS_CREDENTIAL_PATH = f'{HOME_DIR}/.aws/credentials'
PROFILE_DIR         = f'/artifacts/profile'
ARTIFACT_DIR        = f'/artifacts/artifact'
SHARED_DIR          = f'/artifacts/shared'
PULL_SECRET_FILE    = f'{HOME_DIR}/.local/pull-secret.json'
JOB_NAME            = 'periodic-ci-openshift-release-master-nightly-4.16-e2e-vsphere-ovn'
RELEASE_REPO_PATH   = f'{HOME_DIR}/code/release'
BASE_DOMAIN         = "vmc-ci.devcluster.openshift.com"
PROVIDER_NAME       = 'vsphere'
AWS_REGION          = 'us-west-2'
MACHINE_CIDR        = '10.0.0.0/16'
CCM_NAMESPACE       = 'openshift-cloud-controller-manager'

os.environ["CLUSTER_PROFILE_NAME"] = "vsphere-elastic"
os.environ["LEASED_RESOURCE"] = "vsphere-elastic-1"
os.environ["JOB_NAME_SAFE"] = "openshift-e2e-vsphere"
os.environ["MULTI_NIC_IPI"] = ""
os.environ["POPULATE_LEGACY_SPEC"] = ""
os.environ["RELEASE_IMAGE_LATEST_FROM_BUILD_FARM"] = "quay.io/openshift-release-dev/ocp-release:4.16.12-x86_64"
os.environ["RELEASE_IMAGE_INITIAL"] = "quay.io/openshift-release-dev/ocp-release:4.16.12-x86_64"
os.environ["CONTROL_PLANE_REPLICAS"] = "3"
os.environ["COMPUTE_NODE_REPLICAS"] = "3"
os.environ["PULL_THROUGH_CACHE"] = "enabled"
os.environ["SIZE_VARIANT"] = ""
os.environ["KUBECONFIG"] = ""
os.environ["CLUSTER_TYPE"] = "vsphere"

skipSteps=["ipi-install-rbac", "openshift-cluster-bot-rbac"]

