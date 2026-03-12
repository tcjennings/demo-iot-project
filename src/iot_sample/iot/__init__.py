"""Core IoT application logic for sensor data acquisition and message production.

This module implements the primary application workflow that simulates an edge IoT device
reading from hardware sensors and publishing measurements to a message queue. The architecture
demonstrates async task coordination, buffer management, and the complete data pipeline from
raw sensor bytes to serialized protobuf messages.

Key Components
--------------
reader : module
    Implements the sensor reading loop that samples an emulated sensor at a configured
    frequency and appends packed binary readings to a shared buffer. Demonstrates async
    I/O patterns for periodic sensor polling.

producer : module
    Implements the message producer loop that consumes readings from the buffer, unpacks
    them from binary format, converts to protobuf messages, and publishes to Kafka.
    Demonstrates async message queue integration and protobuf serialization.

state : module
    Provides a global State singleton that coordinates communication between the reader
    and producer tasks through a rolling deque buffer. Also holds protobuf descriptors,
    dynamically-generated Pydantic models, and task references for lifecycle management.

settings : module
    Defines application configuration using Pydantic BaseSettings with environment variable
    support (IOT_ prefix). Controls sensor type, sampling frequency, buffer size, and
    logging level.

sensors : package
    Contains emulated IoT sensor implementations that produce packed binary data mimicking
    real hardware sensors. Each sensor type corresponds to a protobuf message definition
    and emits measurements in a specific binary format using struct.pack.

Architecture Notes
------------------
This module represents the application-specific business logic distinct from generic
utilities (lib/) and entry points (libexec/). The two async tasks (reader and producer)
run concurrently within FastAPI's lifespan context, communicating through the shared
state buffer. This design demonstrates separation of concerns: sensor interface logic
is isolated from message queue logic, with the state object providing the integration
point.

The module's design intentionally showcases several patterns for portfolio/demonstration
purposes: async task coordination, buffer-based producer-consumer patterns, dynamic
protobuf message handling based on configuration, and the integration of multiple
independent components (sensors, serialization, message queues) into a cohesive pipeline.
"""
