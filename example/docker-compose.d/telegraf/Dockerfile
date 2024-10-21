ARG TELEGRAF_IMAGE
ARG UV_VERSION

FROM $TELEGRAF_IMAGE

RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    curl \
    git \
    && apt-get clean

# Download and install uv
ADD https://astral.sh/uv/${UV_VERSION}/install.sh /uv-installer.sh

RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH=/root/.cargo/bin:$PATH

ADD pyproject.toml uv.lock /app/

WORKDIR /app

RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"
