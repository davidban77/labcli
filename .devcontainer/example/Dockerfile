FROM debian:bookworm-slim AS builder

ENV CARGO_HOME="/opt/.cargo"

SHELL [ "/bin/bash", "-o", "pipefail", "-c" ]

WORKDIR /opt

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates curl

# Run uv installer
RUN curl -LsSf https://astral.sh/uv/install.sh | sh


FROM mcr.microsoft.com/vscode/devcontainers/base:bookworm

LABEL org.opencontainers.image.source="https://github.com/davidban77/labcli"
LABEL org.opencontainers.image.description="LabCLI devcontainer example image."

ENV CARGO_HOME="/opt/.cargo"
ENV PATH="$CARGO_HOME/bin/:$PATH"
ENV PYTHONUNBUFFERED=True
ENV UV_LINK_MODE=copy

WORKDIR /opt

COPY --from=builder --chown=vscode: $CARGO_HOME $CARGO_HOME

RUN echo "deb [trusted=yes] https://netdevops.fury.site/apt/ /" | \
    tee -a /etc/apt/sources.list.d/netdevops.list

# install containerlab and tools
RUN apt update && \
    apt install -y --no-install-recommends containerlab \
    curl \
    ca-certificates \
    btop \
    gh \
    iputils-ping \
    tcpdump \
    iproute2 \
    qemu-kvm \
    dnsutils \
    telnet

# Install gNMIc
RUN bash -c "$(curl -sL https://get-gnmic.openconfig.net)"

# Add empty docker config files to avoid clab warnings for root user
RUN mkdir -p /root/.docker && echo "{}" > /root/.docker/config.json

# Maintain SSH_AUTH_SOCK env var when using sudo
RUN mkdir -p /etc/sudoers.d && echo 'Defaults env_keep += "SSH_AUTH_SOCK"' > /etc/sudoers.d/ssh_auth_sock

# vscode user is created in the MS devcontainer image
USER vscode

ENV PATH="$PATH:/home/vscode/.local/bin:/home/vscode/.venv/bin"

# Create ssh key for vscode user to enable passwordless ssh to devices
RUN ssh-keygen -t ecdsa -b 256 -N "" -f ~/.ssh/id_ecdsa && \
    mkdir -p /home/vscode/.docker && \
    echo "{}" > /home/vscode/.docker/config.json