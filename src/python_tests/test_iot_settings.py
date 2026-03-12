"""Tests for the iot.settings module.

These tests validate the Pydantic settings configuration, including default values,
environment variable parsing, and field validation for the IoT application settings.
"""

from uuid import UUID

import pytest

from iot_sample.iot.settings import _settings


class TestSettings:
    """Test suite for IoT application settings."""

    def test_default_values(self, monkeypatch):
        """Test that settings have correct default values."""
        # Clear any environment variables that might interfere
        monkeypatch.delenv("IOT_SENSOR_TYPE", raising=False)
        monkeypatch.delenv("IOT_LOGGING_LEVEL", raising=False)

        settings = _settings()

        assert settings.logging_level == "INFO"
        assert isinstance(settings.sensor_id, UUID)
        assert settings.sensor_type == "IOT_SENSOR_TYPE_UNSPECIFIED"
        assert settings.frequency == 1
        assert settings.buffer_time_sec == 10

    def test_sensor_id_is_uuid(self):
        """Test that sensor_id is a valid UUID."""
        settings = _settings()

        # Should be a valid UUID object
        assert isinstance(settings.sensor_id, UUID)
        # Should have 32 hex digits
        assert len(settings.sensor_id.hex) == 32

    def test_env_variable_override_logging_level(self, monkeypatch):
        """Test that IOT_LOGGING_LEVEL environment variable overrides default."""
        monkeypatch.setenv("IOT_LOGGING_LEVEL", "DEBUG")
        settings = _settings()

        assert settings.logging_level == "DEBUG"

    def test_env_variable_override_sensor_type(self, monkeypatch):
        """Test that IOT_SENSOR_TYPE environment variable overrides default."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        settings = _settings()

        assert settings.sensor_type == "IOT_SENSOR_TYPE_TEMP_HUMIDITY"

    def test_env_variable_override_frequency(self, monkeypatch):
        """Test that IOT_FREQUENCY environment variable overrides default."""
        monkeypatch.setenv("IOT_FREQUENCY", "5")
        settings = _settings()

        assert settings.frequency == 5

    def test_env_variable_override_buffer_time(self, monkeypatch):
        """Test that IOT_BUFFER_TIME_SEC environment variable overrides default."""
        monkeypatch.setenv("IOT_BUFFER_TIME_SEC", "30")
        settings = _settings()

        assert settings.buffer_time_sec == 30

    def test_env_variable_override_sensor_id(self, monkeypatch):
        """Test that IOT_SENSOR_ID environment variable overrides default."""
        test_uuid = "12345678-1234-5678-1234-567812345678"
        monkeypatch.setenv("IOT_SENSOR_ID", test_uuid)
        settings = _settings()

        assert str(settings.sensor_id) == test_uuid

    @pytest.mark.parametrize(
        "frequency,buffer_time",
        [
            (1, 10),
            (10, 5),
            (100, 1),
            (5, 60),
        ],
    )
    def test_various_frequency_buffer_combinations(
        self, frequency, buffer_time, monkeypatch
    ):
        """Test settings with various frequency and buffer time combinations."""
        monkeypatch.setenv("IOT_FREQUENCY", str(frequency))
        monkeypatch.setenv("IOT_BUFFER_TIME_SEC", str(buffer_time))
        settings = _settings()

        assert settings.frequency == frequency
        assert settings.buffer_time_sec == buffer_time
