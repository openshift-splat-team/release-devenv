FROM nested-environment-builder:latest

USER root
RUN dnf install -y jq git bind-utils unzip

USER default
COPY . .

#RUN pip install ansible envsubst pyvmomi
#RUN pip install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git

RUN curl -O -L https://github.com/mikefarah/yq/releases/download/v4.44.3/yq_linux_amd64
RUN chmod +x yq_linux_amd64
RUN mkdir -p /opt/app-root/src/.local/bin
RUN mv yq_linux_amd64 /opt/app-root/src/.local/bin/yq
RUN pip install python-dotenv requests