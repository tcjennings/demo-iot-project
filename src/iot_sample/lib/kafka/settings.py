"""Kafka producer and consumer settings."""

from typing import Annotated, Literal

from dotenv import load_dotenv
from pydantic import DirectoryPath, Field, FilePath, StrictBool, StringConstraints
from pydantic_settings import BaseSettings, SettingsConfigDict

from ...iot.settings import settings as iot_settings

# Although pydantic-settings is capable of including a dotenv file in its
# initialization, using load_dotenv() directly grants us the option of
# searching upward through the filesystem hierarchy to find a .dotenv to load
load_dotenv()


class _consumer_settings(BaseSettings):
    """A BaseSettings class for Kafka consumer-specific parameters."""

    model_config = SettingsConfigDict(env_prefix="KAFKA_CONSUMER_")

    auto_offset_reset: Literal["earliest", "latest"] = Field(
        default="earliest", serialization_alias="auto.offset.reset"
    )

    enable_auto_commit: StrictBool = Field(
        default=True, serialization_alias="enable.auto.commit"
    )

    auto_commit_interval_ms: int = Field(
        default=5_000, serialization_alias="auto.commit.interval.ms"
    )

    group_id: str | None = Field(default=None, serialization_alias="group.id")

    group_protocol: Literal["classic", "consumer"] = Field(
        default="classic",
        serialization_alias="group.protocol",
    )

    session_timeout_ms: int = Field(
        default=45_000,
        serialization_alias="session.timeout.ms",
    )

    heartbeat_interval_ms: int = Field(
        default=3_000,
        serialization_alias="heartbeat.interval.ms",
    )

    # The tuning parameters allow one to optimize a Consumer for latency or
    # throughput. The default values tend to prioritize latency.
    fetch_min_bytes: int = Field(
        default=1,
        serialization_alias="fetch.min.bytes",
        description="Minimum number of bytes the broker responds with.",
    )
    fetch_max_bytes: int = Field(
        default=52_428_800,
        serialization_alias="fetch.max.bytes",
        description="The maximum size of a fetch request (batch of messages).",
    )
    fetch_max_wait_ms: int = Field(
        default=500,
        serialization_alias="fetch.max.wait.ms",
        description="Maximum blocking time waiting for `fetch_min_bytes` of data.",
    )
    fetch_message_max_bytes: int = Field(
        default=1_048_576,
        serialization_alias="fetch.message.max.bytes",
        description="Initial maximum number of bytes per topic+partition to request when fetching messages from the broker.",
    )
    max_poll_interval_ms: int = Field(
        default=300_000,
        serialization_alias="max.poll.interval.ms",
        description="Max time between consumer polls, after which the consumer is considered failed and the group rebalances.",
    )

    # The underlying local queue is part of librdkafka's architecture; at the
    # application level, Kafka Clients get their data from the local queue.
    # At the library level, librdkafka pre-fetches data to keep these queues full.

    queued_min_messages: int = Field(
        default=1_000_000,
        serialization_alias="queued.min.messages",
        description="Minimum number of messages per topic+partition librdkafka tries to maintain in the local consumer queue.",
    )

    queued_max_messages_kbytes: int = Field(
        default=65_536,
        serialization_alias="queued.max.messages.kbytes",
        description="Maximum number of kilobytes of queued pre-fetched messages in the local consumer queue.",
    )


class _producer_settings(BaseSettings):
    """A BaseSettings class for Kafka producer-specific parameters."""

    model_config = SettingsConfigDict(env_prefix="KAFKA_PRODUCER_")

    queue_buffering_max_ms: int = Field(
        default=0, serialization_alias="queue.buffering.max.ms"
    )


class _kafka_settings(BaseSettings):
    """A BaseSettings class for common Kafka parameters.

    These may be set by environment variables as `KAFKA_<setting_name>` and
    each <setting_name> is further transformed into an `rdkafka` configuration
    key as needed.

    Fields with `exclude=True` will be excluded from serialization, i.e., when this settings
    model is serialized to configure a Kafka client, such a field is superfluous.

    Notes
    -----
    The optional ssl-related fields must be populated in order to support mTLS authentication
    with a Kafka broker; otherwise the client will fall back to unauthenticated access. Without
    at least the `ssl_ca_location` configured, SSL connections to brokers will fail if the broker
    cert cannot be verified.
    """

    model_config = SettingsConfigDict(env_prefix="KAFKA_", case_sensitive=False)

    bootstrap_servers: Annotated[
        str, StringConstraints(pattern=r"^(([^:,\s]+?:[\d]+),?)+$")
    ] = Field(default="localhost:9092", serialization_alias="bootstrap.servers")
    client_id: str = Field(
        default=str(iot_settings.sensor_id), serialization_alias="client.id"
    )
    enable_ssl_certification_verification: StrictBool = Field(
        default=True, serialization_alias="enable.ssl.certificate.verification"
    )
    # https_ca_location: DirectoryPath | FilePath | Literal["probe"] | None = Field(
    #     default=None,
    #     serialization_alias="https.ca.location",
    #     description="File or directory path to CA certificate(s) for verifying HTTPS endpoints.",
    # )

    security_protocol: Annotated[
        Literal["plaintext", "ssl", "sasl_plaintext", "sasl_ssl"],
        StringConstraints(to_lower=True),
    ] = Field(default="plaintext", serialization_alias="security.protocol")

    ssl_ca_location: DirectoryPath | FilePath | Literal["probe"] | None = Field(
        default=None,
        serialization_alias="ssl.ca.location",
        description="File or directory path to CA certificate(s) for verifying the broker's key.",
    )
    ssl_certificate_location: FilePath | None = Field(
        default=None, serialization_alias="ssl.certificate.location"
    )
    ssl_key_location: FilePath | None = Field(
        default=None, serialization_alias="ssl.key.location"
    )
    statistics_interval_ms: int = Field(
        default=30_000, serialization_alias="statistics.interval.ms"
    )
    topic: str | None = Field(default=None, exclude=True)
    message_key: str | None = Field(default=None, exclude=True)


kafka_settings = _kafka_settings()
producer_settings = _producer_settings()
consumer_settings = _consumer_settings()
