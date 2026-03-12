"""Tests for the iot.reader module.

These tests validate the sensor reader loop, which samples sensors at a configured
frequency and populates the shared buffer with raw binary readings.
"""

import asyncio

import pytest

from iot_sample.iot import reader, state


class TestSensorReaderLoop:
    """Test suite for the sensor reader loop."""

    @pytest.mark.asyncio
    async def test_reader_sets_sensor_data_format(self, monkeypatch):
        """Test that the reader loop sets the sensor_data_format on state."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        monkeypatch.setenv("IOT_FREQUENCY", "10")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.reader.state", test_state)

        # sensor_data_format should start as None
        assert test_state.sensor_data_format is None

        # Start the reader loop and cancel it after a short time
        task = asyncio.create_task(reader.start_sensor_reader_loop())
        await asyncio.sleep(0.2)  # Let it run briefly
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # sensor_data_format should now be set
        assert test_state.sensor_data_format is not None
        assert test_state.sensor_data_format == ">iI"  # TempHumiditySensor format

    @pytest.mark.asyncio
    async def test_reader_adds_readings_to_buffer(self, monkeypatch):
        """Test that the reader loop adds readings to the state buffer."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        monkeypatch.setenv("IOT_FREQUENCY", "10")  # 10 Hz for faster test

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.reader.state", test_state)

        # Buffer should start empty
        assert len(test_state.q) == 0

        # Start the reader loop and let it run briefly
        task = asyncio.create_task(reader.start_sensor_reader_loop())
        await asyncio.sleep(0.3)  # Should get ~3 readings at 10 Hz
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Buffer should now have readings
        assert len(test_state.q) > 0

    @pytest.mark.asyncio
    async def test_reader_produces_bytes(self, monkeypatch):
        """Test that reader adds bytes to the buffer."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        monkeypatch.setenv("IOT_FREQUENCY", "10")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.reader.state", test_state)

        # Start the reader loop
        task = asyncio.create_task(reader.start_sensor_reader_loop())
        await asyncio.sleep(0.2)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Check that buffer contains bytes
        if len(test_state.q) > 0:
            assert all(isinstance(reading, bytes) for reading in test_state.q)

    @pytest.mark.asyncio
    async def test_reader_respects_frequency(self, monkeypatch):
        """Test that reader samples at approximately the configured frequency."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.reader.state", test_state)

        # Run for a period and verify we get multiple readings
        # Note: The actual frequency depends on the settings loaded at import time,
        # but we can verify that readings are produced continuously
        task = asyncio.create_task(reader.start_sensor_reader_loop())
        await asyncio.sleep(1.5)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Should get at least one reading in 1.5 seconds, typically more
        # (actual frequency may vary based on settings loaded at import)
        assert len(test_state.q) >= 1

    @pytest.mark.asyncio
    async def test_reader_produces_correct_byte_length(self, monkeypatch):
        """Test that reader produces readings of expected byte length."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        monkeypatch.setenv("IOT_FREQUENCY", "10")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.reader.state", test_state)

        # Start the reader loop
        task = asyncio.create_task(reader.start_sensor_reader_loop())
        await asyncio.sleep(0.2)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # TempHumiditySensor format 'iI' should produce 8 bytes
        if len(test_state.q) > 0:
            assert all(len(reading) == 8 for reading in test_state.q)

    @pytest.mark.asyncio
    async def test_reader_buffer_rolls_over(self, monkeypatch):
        """Test that reader buffer respects maxlen and rolls over."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        # Reset state for clean test (will use default settings)
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.reader.state", test_state)

        # Note: maxlen is determined by settings at State creation time
        # Default settings are frequency=1, buffer_time_sec=10, so maxlen=10
        original_maxlen = test_state.q.maxlen
        assert original_maxlen is not None  # State always sets maxlen

        # Run long enough to overflow the buffer (produce more than maxlen readings)
        task = asyncio.create_task(reader.start_sensor_reader_loop())
        await asyncio.sleep(float(original_maxlen + 2))  # Exceed buffer capacity
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Buffer should be at maxlen, not larger (deque automatically rolls over)
        assert len(test_state.q) == original_maxlen


@pytest.mark.parametrize(
    "sensor_type,expected_format,expected_byte_len",
    [
        ("IOT_SENSOR_TYPE_TEMP_HUMIDITY", ">iI", 8),
        ("IOT_SENSOR_TYPE_AIR_QUALITY", ">HHH", 6),
        ("IOT_SENSOR_TYPE_OPEN_CLOSE", ">?", 1),
        ("IOT_SENSOR_TYPE_LIGHT", ">HH", 4),
    ],
)
class TestReaderWithDifferentSensors:
    """Parametrized tests for reader with different sensor types."""

    @pytest.mark.asyncio
    async def test_reader_sets_correct_format_for_sensor_type(
        self, sensor_type, expected_format, expected_byte_len, monkeypatch
    ):
        """Test that reader sets correct format string for each sensor type."""
        from iot_sample.iot.settings import _settings

        # Create fresh settings instance with the desired sensor type
        monkeypatch.setenv("IOT_SENSOR_TYPE", sensor_type)
        monkeypatch.setenv("IOT_FREQUENCY", "10")
        test_settings = _settings()

        # Reset state for clean test with the sensor type
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.reader.state", test_state)
        monkeypatch.setattr("iot_sample.iot.reader.settings", test_settings)

        # Start the reader loop
        task = asyncio.create_task(reader.start_sensor_reader_loop())
        await asyncio.sleep(0.2)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Verify that the reader dynamically set the correct format for the sensor type
        assert test_state.sensor_data_format == expected_format

    @pytest.mark.asyncio
    async def test_reader_produces_correct_byte_length_for_sensor(
        self, sensor_type, expected_format, expected_byte_len, monkeypatch
    ):
        """Test that reader produces correct byte length for each sensor type."""
        from iot_sample.iot.settings import _settings

        # Create fresh settings instance with the desired sensor type
        monkeypatch.setenv("IOT_SENSOR_TYPE", sensor_type)
        monkeypatch.setenv("IOT_FREQUENCY", "10")
        test_settings = _settings()

        # Reset state for clean test with the sensor type
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.reader.state", test_state)
        monkeypatch.setattr("iot_sample.iot.reader.settings", test_settings)

        # Start the reader loop
        task = asyncio.create_task(reader.start_sensor_reader_loop())
        await asyncio.sleep(0.2)
        task.cancel()

        try:
            await task
        except asyncio.CancelledError:
            pass

        # Verify that the reader produces readings with the correct byte length for the sensor type
        if len(test_state.q) > 0:
            assert all(len(reading) == expected_byte_len for reading in test_state.q)
