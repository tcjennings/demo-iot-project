"""A module for defining a Kafka consumer object using the Confluent Kafka package,
which is a full-featured Kafka client based on the `rdkafka` library and supports
custom serializers and deserializers.
"""

from confluent_kafka import Consumer, KafkaError, ThrottleEvent, TopicPartition

from .settings import consumer_settings, kafka_settings


class IotConsumer(Consumer):
    running: bool

    @classmethod
    def error_cb(cls, err: KafkaError): ...

    @classmethod
    def on_commit(cls, err: KafkaError | None, tp: list[TopicPartition]): ...

    @classmethod
    def stats_cb(cls, json_str: str):
        """Callback for stats reporting.

        If `statistics.interval.ms` is configured on the client, this callback
        will be invoked when `poll()` is called.

        Arguments
        ---------
        json_str : str
            The string representation of a JSON document containing Kafka Client
            statistics.

        See Also
        --------
        https://github.com/confluentinc/librdkafka/blob/master/STATISTICS.md
        """
        ...

    @classmethod
    def throttle_cb(cls, evt: ThrottleEvent): ...

    def __enter__(self):
        """Allows use of the consumer as a context manager."""
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return self.close()


def get_consumer():
    """Constructs and returns a configured Kafka consumer."""
    return IotConsumer(
        **consumer_settings.model_dump(by_alias=True),
        **kafka_settings.model_dump(by_alias=True),
        stats_cb=IotConsumer.stats_cb,
        error_cb=IotConsumer.error_cb,
        on_commit=IotConsumer.on_commit,
    )
