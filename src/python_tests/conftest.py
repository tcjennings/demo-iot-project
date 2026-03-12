"""Pytest configuration and shared fixtures for iot_sample tests.

This module provides common test fixtures and pytest configuration used across
all test modules in the test suite.
"""

import os

import pytest

# Set default environment variables before any modules are imported
# This ensures the global state singleton can be created successfully
os.environ.setdefault("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
os.environ.setdefault("IOT_LOGGING_LEVEL", "ERROR")


@pytest.fixture(autouse=True)
def reset_environment(monkeypatch):
    """Fixture to ensure clean environment for each test.

    This autouse fixture ensures that tests don't inherit environment variables
    from the shell or from previous tests, providing test isolation.
    """
    # Set minimal default environment to avoid state pollution
    monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
    monkeypatch.setenv("IOT_LOGGING_LEVEL", "ERROR")  # Reduce noise in tests


@pytest.fixture
def temp_humidity_sensor_reading():
    """Fixture providing a sample temperature/humidity sensor reading."""
    from struct import pack

    # temperature_c=20, rel_hum_pct=35
    return pack(">iI", 20, 35)


@pytest.fixture
def air_quality_sensor_reading():
    """Fixture providing a sample air quality sensor reading."""
    from struct import pack

    # co2_ppm=800, co_ppm=3, o3_ppb=50
    return pack(">HHH", 800, 3, 50)


@pytest.fixture
def open_close_sensor_reading():
    """Fixture providing a sample open/close sensor reading."""
    from struct import pack

    # open=True
    return pack(">?", True)


@pytest.fixture
def light_sensor_reading():
    """Fixture providing a sample light sensor reading."""
    from struct import pack

    # lumens=1000, color_temp_k=3500
    return pack(">HH", 1000, 3500)
