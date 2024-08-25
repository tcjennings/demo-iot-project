# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.12

################################################################################
# BUILDER STAGE
################################################################################
# The goal of a builder stage is to create a python environment where
# our application dependencies are installed in such a way that they
# can be copied into a runtime image that does not need to have package
# managers or any other components unrelated to the application runtime
################################################################################
FROM --platform=$TARGETPLATFORM python:${PYTHON_VERSION} as builder
ARG PYTHON_VERSION
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS
ENV UV_PYTHON=cpython@${PYTHON_VERSION}
ENV UV_LINK_MODE=copy
ENV UV_PYTHON_INSTALL_DIR=/opt/python/dist
ENV PATH="/root/.cargo/bin/:$PATH"

# Obtain the uv tool
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN <<ENDRUN
  sh /uv-installer.sh
ENDRUN

# Use uv to install a standalone cpython distribution and
# the project dependencies into a venv
WORKDIR /opt/python
COPY uv.lock pyproject.toml .
RUN <<ENDRUN
  set -e
  uv venv --relocatable --allow-existing --python-preference only-managed
  uv sync --frozen --no-install-project --no-dev
ENDRUN

################################################################################
# RUNTIME STAGE
################################################################################
# Based on a "distroless" image with minimal system surface area. Includes base
# debian12 libraries plus libgcc. The debug tag includes a busybox shell;
# use "latest" to omit this for production
################################################################################
FROM --platform=$TARGETPLATFORM gcr.io/distroless/cc-debian12:debug as runtime

# copies the standalone python installation and the installed project dependencies
# from the builder image.
WORKDIR /opt/python
COPY --from=builder /opt/python .
ENV PATH=/opt/python/bin:$PATH

# copies the application package into a working directory associated with a nonroot user
# sets the container entrypoint to run python with the module flag; this ensures the
# correct resolution of any relative imports.
WORKDIR /home/nonroot
ENTRYPOINT ["/opt/python/.venv/bin/python3", "-m"]
COPY --chown=nonroot:nonroot ./src/python ./app

# Switches to the nonroot user provided by the runtime base image and sets the command args
# for the entrypoint to the module name of the application's entrypoint
USER nonroot
CMD ["app.libexec.server"]
