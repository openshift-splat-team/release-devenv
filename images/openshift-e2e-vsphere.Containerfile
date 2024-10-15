FROM registry.access.redhat.com/ubi9/ubi@sha256:b00d5990a00937bd1ef7f44547af6c7fd36e3fd410e2c89b5d2dfc1aff69fe99

WORKDIR /usr/app/src

RUN dnf install -y python jq

RUN python3 -m ensurepip --default-pip
RUN pip install pyyaml envsubst python-dotenv

RUN curl -O https://mirror.openshift.com/pub/openshift-v4/clients/ocp/4.16.12/openshift-client-linux-4.16.12.tar.gz
RUN tar xf openshift-client-linux-4.16.12.tar.gz
RUN mv oc /usr/local/bin
RUN mv kubectl /usr/local/bin
RUN rm openshift-client-linux-4.16.12.tar.gz

RUN curl -O -L https://github.com/vmware/govmomi/releases/download/v0.30.7/govc_Linux_x86_64.tar.gz
RUN tar xf govc_Linux_x86_64.tar.gz
RUN mv govc /usr/local/bin
RUN rm govc_Linux_x86_64.tar.gz

RUN curl -O -L https://mirror.openshift.com/pub/openshift-v4/clients/ocp/4.16.16/openshift-install-linux.tar.gz
RUN tar xf openshift-install-linux.tar.gz
RUN mv openshift-install /usr/local/bin
RUN rm openshift-install-linux.tar.gz

RUN curl -O -L https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64
RUN chmod +x yq_linux_amd64
RUN mv yq_linux_amd64 /usr/local/bin/yq

COPY . .