"""Kafka producer and consumer settings."""

from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ...iot.settings import settings as iot_settings

# Although pydantic-settings is capable of including a dotenv file in its
# initialization, using load_dotenv() directly grants us the option of
# searching upward through the filesystem hierarchy to find a .dotenv to load
load_dotenv()


class _consumer_settings(BaseSettings):
    """A BaseSettings class for Kafka consumer-specific parameters."""

    model_config = SettingsConfigDict(env_prefix="KAFKA_CONSUMER_")


class _producer_settings(BaseSettings):
    """A BaseSettings class for Kafka producer-specific parameters."""

    model_config = SettingsConfigDict(env_prefix="KAFKA_PRODUCER_")

    queue_buffering_max_ms: int = Field(
        default=0, serialization_alias="queue.buffering.max.ms"
    )

    statistics_interval_ms: int = Field(
        default=30_000, serialization_alias="statistics.interval.ms"
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

    bootstrap_servers: str = Field(
        default="kafka:9092", serialization_alias="bootstrap.servers"
    )
    client_id: str = Field(
        default=str(iot_settings.sensor_id), serialization_alias="client.id"
    )
    enable_ssl_certification_verification: bool = Field(
        default=True, serialization_alias="enable.ssl.certificate.verification"
    )
    security_protocol: str = Field(
        default="SSL", serialization_alias="security.protocol"
    )
    ssl_ca_location: Optional[str] = Field(
        default=None, serialization_alias="ssl.ca.location"
    )
    ssl_certificate_location: Optional[str] = Field(
        default=None, serialization_alias="ssl.certificate.location"
    )
    ssl_key_location: Optional[str] = Field(
        default=None, serialization_alias="ssl.key.location"
    )
    topic: Optional[str] = Field(default=None, exclude=True)
    message_key: Optional[str] = Field(default=None, exclude=True)


kafka_settings = _kafka_settings()
producer_settings = _producer_settings()
consumer_settings = _consumer_settings()
