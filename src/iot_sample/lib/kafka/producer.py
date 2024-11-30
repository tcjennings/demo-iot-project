"""A module for defining a Kafka producer object using the Confluent Kafka package,
which is a full-featured Kafka client based on the `rdkafka` library and supports
custom serializers and deserializers.

The producer for this IOT application will support minimal custom producer configuration
and will instead default to using low-latency parameters including minimal wait time
in the producer buffer, 0 acks, and no expectation of batching or compression.

Any messages produced to a Kafka topic will be keyed using the sensor ID as set by configuration
settings.
"""

from confluent_kafka import KafkaException, Message, Producer

from ..logging import logger
from .settings import kafka_settings, producer_settings


class IotProducer(Producer):
    """A subclass of a Confluent Kafka Producer.

    We use this opportunity to fine-tune the interface of the producer so we can have a stable
    reference interface for producing messages.
    """

    def produce(self, message: bytes):
        """Produce a message from provided bytes."""
        try:
            super().produce(
                topic=kafka_settings.topic,
                value=message,
                key=kafka_settings.message_key,
                on_delivery=self.__class__.delivery_cb,
            )
        except KafkaException as e:
            logger.error(e)

        # A non-blocking poll of the producer queue to propogate delivery notifications
        self.poll(0)

    @classmethod
    def delivery_cb(cls, err, msg: Message):
        """A delivery callback function, triggered by the producer library for every
        message"""
        if err is not None:
            logger.warning(f"Failed to deliver message: {err}")

    @classmethod
    def stats_cb(cls, json_str):
        """A callback method for handling statistics reporting."""
        logger.debug(json_str)

    def shutdown(self):
        """Called when we are done with the producer."""
        self.flush()

    def __enter__(self):
        """Allows use of the producer as a context manager."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.shutdown()


def get_producer():
    """Constructs and returns a configured Kafka producer."""
    return IotProducer(
        **producer_settings.model_dump(by_alias=True),
        **kafka_settings.model_dump(by_alias=True),
        stats_cb=IotProducer.stats_cb,
    )
