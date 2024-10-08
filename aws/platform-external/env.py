CLUSTER_NAME        = '<user>-external'
HOME_DIR            = '/home/<user>'
RELEASE_IMAGE       = 'quay.io/openshift-release-dev/ocp-release:4.16.12-x86_64'
SSH_PUBLIC_KEY      = f'{HOME_DIR}/.ssh/id_rsa.pub'
AWS_CREDENTIAL_PATH = f'{HOME_DIR}.aws/credentials'
PROFILE_DIR         = f'/tmp/{CLUSTER_NAME}/profile'
ARTIFACT_DIR        = f'/tmp/{CLUSTER_NAME}/artifact'
SHARED_DIR          = f'/tmp/{CLUSTER_NAME}/shared'
PULL_SECRET_FILE    = f'{HOME_DIR}/.local/pull-secret.json'
JOB_NAME            = 'periodic-ci-openshift-release-master-nightly-4.16-e2e-external-aws-ccm'
RELEASE_REPO_PATH   = f'{HOME_DIR}/code/release'
BASE_DOMAIN         = "vmc-ci.devcluster.openshift.com"
PROVIDER_NAME       = 'aws'
AWS_REGION          = 'us-west-2'
MACHINE_CIDR        = '10.0.0.0/16'
CCM_NAMESPACE       = 'openshift-cloud-controller-manager'

skipSteps=["ipi-install-rbac", "openshift-cluster-bot-rbac"]

