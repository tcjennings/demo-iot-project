"""Tests for the iot.sensors.emulated module.

These tests validate the emulated IoT sensor implementations, ensuring they produce
correctly formatted binary data that matches their protobuf message definitions.
"""

from struct import unpack

import pytest

from iot_sample.iot.sensors.emulated import (
    AirQualitySensor,
    LightSensor,
    OpenCloseSensor,
    TempHumiditySensor,
)


class TestIotSensorBase:
    """Test suite for the base IotSensor abstract class behavior."""

    def test_byte_order_is_big_endian(self):
        """Test that sensors use big-endian (network) byte order."""
        # All sensor classes should inherit the same byte order
        assert TempHumiditySensor.byte_order == ">"
        assert AirQualitySensor.byte_order == ">"
        assert OpenCloseSensor.byte_order == ">"
        assert LightSensor.byte_order == ">"


class TestTempHumiditySensor:
    """Test suite for TempHumiditySensor."""

    def test_format_string(self):
        """Test that format string is correct for temperature/humidity data."""
        sensor = TempHumiditySensor()
        # 'i' = signed int (temperature), 'I' = unsigned int (humidity)
        assert sensor.format_string == "iI"

    def test_get_measurement_returns_tuple(self):
        """Test that get_measurement returns a tuple of two values."""
        sensor = TempHumiditySensor()
        measurement = sensor.get_measurement()

        assert isinstance(measurement, tuple)
        assert len(measurement) == 2

    def test_get_measurement_value_ranges(self):
        """Test that measurements are within expected ranges."""
        sensor = TempHumiditySensor()

        # Test multiple readings to verify range constraints
        for _ in range(10):
            temp_c, rel_hum_pct = sensor.get_measurement()

            # Temperature should be 0-22°C based on emulated.py
            assert 0 <= temp_c <= 22
            # Humidity should be 20-45% based on emulated.py
            assert 20 <= rel_hum_pct <= 45

    def test_sensor_call_returns_bytes(self):
        """Test that calling the sensor returns packed binary data."""
        sensor = TempHumiditySensor()
        reading = sensor()

        assert isinstance(reading, bytes)
        # 'iI' should produce 8 bytes (4 + 4)
        assert len(reading) == 8

    def test_sensor_output_can_be_unpacked(self):
        """Test that sensor output can be unpacked with the format string."""
        sensor = TempHumiditySensor()
        reading = sensor()

        # Should be able to unpack with the sensor's format
        unpacked = unpack(f"{sensor.byte_order}{sensor.format_string}", reading)

        assert len(unpacked) == 2
        assert isinstance(unpacked[0], int)  # temperature
        assert isinstance(unpacked[1], int)  # humidity


class TestAirQualitySensor:
    """Test suite for AirQualitySensor."""

    def test_format_string(self):
        """Test that format string is correct for air quality data."""
        sensor = AirQualitySensor()
        # 'HHH' = three unsigned shorts (CO2, CO, O3)
        assert sensor.format_string == "HHH"

    def test_get_measurement_returns_tuple(self):
        """Test that get_measurement returns a tuple of three values."""
        sensor = AirQualitySensor()
        measurement = sensor.get_measurement()

        assert isinstance(measurement, tuple)
        assert len(measurement) == 3

    def test_get_measurement_value_ranges(self):
        """Test that measurements are within expected ranges."""
        sensor = AirQualitySensor()

        # Test multiple readings to verify range constraints
        for _ in range(10):
            co2_ppm, co_ppm, o3_ppb = sensor.get_measurement()

            # CO2 should be 700-1000 ppm
            assert 700 <= co2_ppm <= 1000
            # CO should be 2-5 ppm
            assert 2 <= co_ppm <= 5
            # O3 should be 40-60 ppb
            assert 40 <= o3_ppb <= 60

    def test_sensor_call_returns_bytes(self):
        """Test that calling the sensor returns packed binary data."""
        sensor = AirQualitySensor()
        reading = sensor()

        assert isinstance(reading, bytes)
        # 'HHH' should produce 6 bytes (2 + 2 + 2)
        assert len(reading) == 6

    def test_sensor_output_can_be_unpacked(self):
        """Test that sensor output can be unpacked with the format string."""
        sensor = AirQualitySensor()
        reading = sensor()

        unpacked = unpack(f"{sensor.byte_order}{sensor.format_string}", reading)

        assert len(unpacked) == 3
        assert all(isinstance(val, int) for val in unpacked)


class TestOpenCloseSensor:
    """Test suite for OpenCloseSensor."""

    def test_format_string(self):
        """Test that format string is correct for open/close data."""
        sensor = OpenCloseSensor()
        # '?' = bool
        assert sensor.format_string == "?"

    def test_get_measurement_returns_tuple(self):
        """Test that get_measurement returns a tuple of one value."""
        sensor = OpenCloseSensor()
        measurement = sensor.get_measurement()

        assert isinstance(measurement, tuple)
        assert len(measurement) == 1

    def test_get_measurement_value_is_binary(self):
        """Test that measurement is binary (0 or 1)."""
        sensor = OpenCloseSensor()

        # Test multiple readings
        for _ in range(10):
            (open_state,) = sensor.get_measurement()

            # Should be 0 or 1 (boolean converted to int)
            assert open_state in (0, 1)

    def test_sensor_call_returns_bytes(self):
        """Test that calling the sensor returns packed binary data."""
        sensor = OpenCloseSensor()
        reading = sensor()

        assert isinstance(reading, bytes)
        # '?' should produce 1 byte
        assert len(reading) == 1

    def test_sensor_output_can_be_unpacked(self):
        """Test that sensor output can be unpacked with the format string."""
        sensor = OpenCloseSensor()
        reading = sensor()

        unpacked = unpack(f"{sensor.byte_order}{sensor.format_string}", reading)

        assert len(unpacked) == 1
        assert isinstance(unpacked[0], bool)


class TestLightSensor:
    """Test suite for LightSensor."""

    def test_format_string(self):
        """Test that format string is correct for light sensor data."""
        sensor = LightSensor()
        # 'HH' = two unsigned shorts (lumens, color temp)
        assert sensor.format_string == "HH"

    def test_version(self):
        """Test that sensor version is correctly set."""
        sensor = LightSensor()
        assert sensor.version == 2

    def test_get_measurement_returns_tuple(self):
        """Test that get_measurement returns a tuple of two values."""
        sensor = LightSensor()
        measurement = sensor.get_measurement()

        assert isinstance(measurement, tuple)
        assert len(measurement) == 2

    def test_get_measurement_value_ranges(self):
        """Test that measurements are within expected ranges."""
        sensor = LightSensor()

        # Test multiple readings to verify range constraints
        for _ in range(10):
            lumens, color_temp_k = sensor.get_measurement()

            # Lumens should be 600-1500
            assert 600 <= lumens <= 1500
            # Color temp should be 2700-5400 K
            assert 2700 <= color_temp_k <= 5400

    def test_sensor_call_returns_bytes(self):
        """Test that calling the sensor returns packed binary data."""
        sensor = LightSensor()
        reading = sensor()

        assert isinstance(reading, bytes)
        # 'HH' should produce 4 bytes (2 + 2)
        assert len(reading) == 4

    def test_sensor_output_can_be_unpacked(self):
        """Test that sensor output can be unpacked with the format string."""
        sensor = LightSensor()
        reading = sensor()

        unpacked = unpack(f"{sensor.byte_order}{sensor.format_string}", reading)

        assert len(unpacked) == 2
        assert all(isinstance(val, int) for val in unpacked)


@pytest.mark.parametrize(
    "sensor_class,expected_field_count",
    [
        (TempHumiditySensor, 2),
        (AirQualitySensor, 3),
        (OpenCloseSensor, 1),
        (LightSensor, 2),
    ],
)
class TestSensorConsistency:
    """Parametrized tests for consistency across all sensor implementations."""

    def test_sensor_is_callable(self, sensor_class, expected_field_count):
        """Test that all sensors are callable and return bytes."""
        sensor = sensor_class()
        reading = sensor()

        assert isinstance(reading, bytes)
        assert len(reading) > 0

    def test_measurement_tuple_length_matches_format(
        self, sensor_class, expected_field_count
    ):
        """Test that measurement tuple length matches format string field count."""
        sensor = sensor_class()
        measurement = sensor.get_measurement()

        assert len(measurement) == expected_field_count

    def test_sensor_produces_consistent_byte_length(
        self, sensor_class, expected_field_count
    ):
        """Test that sensor produces consistent byte length across calls."""
        sensor = sensor_class()

        # Get multiple readings
        reading1 = sensor()
        reading2 = sensor()
        reading3 = sensor()

        # All readings should have the same length
        assert len(reading1) == len(reading2) == len(reading3)
