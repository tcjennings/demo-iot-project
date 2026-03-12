"""Reusable library components and integrations for the IoT application.

This module provides generic, application-agnostic utilities and third-party service
integrations that support the core IoT business logic. Unlike the `iot` module which
contains application-specific workflow logic, the `lib` module contains reusable components
that could be extracted and used in other projects. The module demonstrates integration
patterns for message queues, protobuf serialization, and configuration management.

Key Submodules
--------------
kafka : package
    Kafka client implementation using confluent-kafka (librdkafka wrapper). Provides
    producer and consumer classes configured for the application's specific needs,
    including mTLS authentication support and low-latency producer settings. Demonstrates
    custom Kafka client configuration, context manager patterns for resource management,
    and protobuf serialization without Confluent Schema Registry.

    Key components:
    - `producer.py`: IotProducer class with simplified interface and get_producer() factory
    - `settings.py`: Pydantic settings for Kafka/rdkafka configuration with KAFKA_ env prefix
    - `serde.py`: Clean-room protobuf serializer/deserializer implementations
    - `consumer.py`: Kafka consumer implementation (for utility/testing purposes)

utility : package
    General-purpose utility functions, particularly for working with protobuf messages
    and bridging between protobuf and Python/Pydantic types. Demonstrates dynamic type
    generation, protobuf descriptor introspection, and binary data unpacking.

    Key module:
    - `proto_tools.py`: Protobuf ↔ Pydantic conversion utilities including:
      - Dynamic Pydantic model generation from protobuf descriptors
      - Sensor payload descriptor lookup based on enum conventions
      - Binary data unpacking and conversion to protobuf messages
      - PROTO_TYPES mapping for protobuf-to-Python type conversion

logging : module
    Simple logging configuration that sets up an application logger with a level
    controlled by the IOT_LOGGING_LEVEL environment variable. Demonstrates centralized
    logging setup that other modules can import and use.

Design Philosophy
-----------------
The lib module follows a "library-first" design where components are built to be
reusable and loosely coupled from application logic. Configuration is externalized
through Pydantic settings with environment variable support, making components
adaptable to different deployment contexts. The Kafka integration demonstrates
preference for explicit configuration over implicit conventions (low-latency settings,
mTLS paths, topic names all configurable).

The protobuf utilities showcase advanced Python techniques: dynamic class generation
via Pydantic's create_model, protobuf descriptor introspection, and the bridging
of multiple type systems (packed binary structs → Pydantic models → protobuf messages).
This multi-stage conversion pattern, while complex, demonstrates handling of systems
that communicate through different serialization formats.

Integration Notes
-----------------
Kafka integration is designed for mTLS authentication, expecting certificate paths
to be provided via environment variables (KAFKA_ssl_ca_location, KAFKA_ssl_certificate_location,
KAFKA_ssl_key_location). The producer is configured for IoT edge device scenarios with
minimal buffering, fire-and-forget semantics (acks=0), and low latency at the expense
of throughput optimization.

The protobuf utilities rely on a specific convention: sensor types are defined in a
protobuf enum where the enum value matches the field number in a oneOf message field.
This allows runtime type resolution based on configuration (IOT_SENSOR_TYPE environment
variable) without conditional logic for each sensor type.
"""
