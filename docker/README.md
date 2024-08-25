# Dockerfile

The main Dockerfile for the project. It uses a multi-stage build pattern
to produce a runtime image containing the application code and its necessary
runtime execution components while minimizing extraneous contents. The runtime
image is based on a Google "distroless" image and a Python is provided through
a "standalone" Python distribution.

# Docker Compose

The `docker-compose.yml` file describes a service stack that provides services with
which the main application may interact. These include:

- Kafka. Using an "all-in-one" image from Confluent, this Kafka service runs a single-node
Kafka broker in KRaFT mode with listeners configured to support connections from within
the Docker network and from the host.

- Localstack. This service provides emulation of any AWS cloud services that may be consumed
by the application or managed by Terraform.
