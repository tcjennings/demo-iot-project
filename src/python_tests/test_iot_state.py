"""Tests for the iot.state module.

These tests validate the State singleton class, which manages shared application state
including the sensor reading buffer, protobuf descriptors, and Pydantic models.
"""

from collections import deque

from google.protobuf.descriptor import FieldDescriptor
from pydantic import BaseModel

from iot_sample.iot.state import State


class TestStateInitialization:
    """Test suite for State class initialization."""

    def test_state_creates_deque(self, monkeypatch):
        """Test that State initializes with a deque buffer."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        assert isinstance(state.q, deque)

    def test_deque_maxlen_based_on_frequency_and_buffer_time(self, monkeypatch):
        """Test that deque maxlen is calculated from frequency and buffer time."""
        from iot_sample.iot.settings import settings

        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        # maxlen should be frequency * buffer_time_sec based on loaded settings
        # Note: Settings are loaded at module import, so we check against actual values
        expected_maxlen = settings.frequency * settings.buffer_time_sec
        assert state.q.maxlen == expected_maxlen

    def test_deque_maxlen_calculation_formula(self, monkeypatch):
        """Test that deque maxlen is calculated using the formula frequency * buffer_time_sec."""
        from iot_sample.iot.settings import settings

        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        # Verify the calculation formula is correct
        # (actual values depend on settings loaded at import time)
        expected_maxlen = settings.frequency * settings.buffer_time_sec
        assert state.q.maxlen == expected_maxlen
        assert (
            state.q.maxlen is not None and state.q.maxlen > 0
        )  # Should always be positive

    def test_sensor_payload_descriptor_is_field_descriptor(self, monkeypatch):
        """Test that sensor_payload_descriptor is a FieldDescriptor."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        assert isinstance(state.sensor_payload_descriptor, FieldDescriptor)

    def test_message_model_is_base_model(self, monkeypatch):
        """Test that message_model is a Pydantic BaseModel class."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        # message_model should be a class that inherits from BaseModel
        assert issubclass(state.message_model, BaseModel)  # type: ignore[arg-type]

    def test_sensor_data_format_initializes_as_none(self, monkeypatch):
        """Test that sensor_data_format starts as None (set by reader task)."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        assert state.sensor_data_format is None

    def test_tasks_initializes_as_empty_set(self, monkeypatch):
        """Test that tasks set starts empty."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        assert isinstance(state.tasks, set)
        assert len(state.tasks) == 0


class TestStateWithSensorType:
    """Test State initialization with sensor types."""

    def test_sensor_payload_descriptor_matches_configured_type(self, monkeypatch):
        """Test that sensor payload descriptor matches the configured sensor type."""
        from iot_proto.iot.v1 import iot_pb2
        from iot_sample.iot.settings import settings

        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        # The field number should match the enum value for the configured type
        enum_value = iot_pb2.IotSensorType.Value(settings.sensor_type)  # type: ignore[attr-defined]
        assert state.sensor_payload_descriptor.number == enum_value

    def test_message_model_has_fields_from_protobuf(self, monkeypatch):
        """Test that message model has fields matching protobuf definition."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        # Get the protobuf message descriptor to check expected fields
        proto_descriptor = state.sensor_payload_descriptor.message_type

        # All protobuf fields should be present in the Pydantic model
        for field_name in proto_descriptor.fields_by_name.keys():
            assert field_name in state.message_model.model_fields

    def test_message_model_name_derived_from_protobuf(self, monkeypatch):
        """Test that message model name comes from the protobuf descriptor."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        # Model name should come from the protobuf descriptor
        expected_name = state.sensor_payload_descriptor.message_type.name
        assert state.message_model.__name__ == expected_name  # type: ignore[attr-defined]
        assert len(expected_name) > 0  # Should have a name


class TestStateBufferOperations:
    """Test State deque buffer operations."""

    def test_can_append_to_buffer(self, monkeypatch):
        """Test that items can be appended to the buffer."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        monkeypatch.setenv("IOT_BUFFER_TIME_SEC", "5")
        monkeypatch.setenv("IOT_FREQUENCY", "1")

        state = State()

        # Append some test data
        state.q.append(b"test_data_1")
        state.q.append(b"test_data_2")

        assert len(state.q) == 2
        assert state.q[0] == b"test_data_1"
        assert state.q[1] == b"test_data_2"

    def test_buffer_respects_maxlen(self, monkeypatch):
        """Test that buffer rolls over when maxlen is exceeded."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        state = State()
        maxlen = state.q.maxlen
        assert maxlen is not None  # State always sets maxlen

        # Add more items than maxlen to trigger rollover
        for i in range(maxlen + 2):
            state.q.append(f"data_{i}".encode())

        # Buffer should be at maxlen, not larger
        assert len(state.q) == maxlen
        # First items should have been pushed out
        assert state.q[0] == b"data_2"  # First two were pushed out
        assert state.q[-1] == f"data_{maxlen + 1}".encode()  # Last item added

    def test_can_popleft_from_buffer(self, monkeypatch):
        """Test that items can be popped from the left of the buffer."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        state.q.append(b"first")
        state.q.append(b"second")

        popped = state.q.popleft()

        assert popped == b"first"
        assert len(state.q) == 1
        assert state.q[0] == b"second"

    def test_sensor_data_format_can_be_set(self, monkeypatch):
        """Test that sensor_data_format can be set after initialization."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        state = State()

        assert state.sensor_data_format is None

        # Set the format string (as the reader task would)
        state.sensor_data_format = ">iI"

        assert state.sensor_data_format == ">iI"
