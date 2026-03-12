"""Serde classes for working with Protobuf messages when producing to or consuming
from Kafka topics.

The `confluent-kafka` package includes similar classes but these are designed to work
with the Confluent Schema Registry and a specific sort of message framing that includes
a 5-byte preamble (a Confluent Magic Byte plus a 4-byte schema id) and a list of proto
descriptor index values.

Instead of using these classes directly or through inheritance, the classes in this module
are closer to a clean-room implementation of a protobuf serde without using the Schema Registry.

This will require and assume that the producer and consumer applications have access to
the same proto message types.
"""

from confluent_kafka.serialization import Deserializer, SerializationContext, Serializer


class ProtoBufSerializer(Serializer):
    """Basic serializer for transmitting a protobuf message as bytes to a Kafka topic.

    Notes
    -----
    Unless noted elsewhere all numeric types are signed and serialization is big-endian.
    """

    def __init__(self, msg_type): ...

    def __call__(self, msg, ctx: SerializationContext | None = None):  # type: ignore[invalid-method-override]
        """
        Converts protobuf message to bytes.

        Parameters
        ----------
        obj : object
            protobuf message to be serialzed

        ctx (SerializationContext): Metadata pertaining to the serialization
            operation

        Raises:
            SerializerError if an error occurs during deserialization

        Returns:
            bytes if obj is not None, otherwise None
        """
        ...


class ProtoBufDeserializer(Deserializer):
    """Basic deserializer for consuming a protobuf message from
    a Kafka topic.
    """

    ...
