from uuid import UUID, uuid4

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class _settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="IOT_")

    logging_level: str = Field(default="INFO")
    sensor_id: UUID = Field(default_factory=uuid4)
    sensor_type: str = Field(default="IOT_SENSOR_TYPE_UNSPECIFIED")
    frequency: int = Field(
        default=1,
        description="The frequency of sensor readings in Hz",
    )
    buffer_time_sec: int = Field(
        default=10,
        description="The size of the sensor reader buffer, in seconds. This, combined with frequency, will determine the size of the application's deque",
    )


settings = _settings()
