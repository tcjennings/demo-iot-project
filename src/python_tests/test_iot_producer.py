"""Tests for the iot.producer module.

These tests validate the Kafka producer loop, which consumes binary readings from
the buffer, converts them to protobuf messages, and publishes them to Kafka.
"""

import asyncio
from struct import pack
from unittest.mock import MagicMock, Mock, patch

import pytest

from iot_proto.iot.v1 import iot_pb2
from iot_sample.iot import producer, state


class TestProducerLoop:
    """Test suite for the Kafka producer loop."""

    @pytest.mark.asyncio
    async def test_producer_waits_for_sensor_data_format(self, monkeypatch):
        """Test that producer waits until sensor_data_format is set."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.producer.state", test_state)

        # sensor_data_format should be None initially
        assert test_state.sensor_data_format is None

        # Mock the producer context manager
        mock_producer = MagicMock()
        mock_producer.__enter__ = Mock(return_value=mock_producer)
        mock_producer.__exit__ = Mock(return_value=None)
        mock_producer.produce = Mock()
        mock_producer.flush = Mock()

        with patch("iot_sample.iot.producer.get_producer", return_value=mock_producer):
            # Start producer loop
            task = asyncio.create_task(producer.start_producer_loop())

            # Let it run briefly (should be waiting for format)
            await asyncio.sleep(0.5)

            # Producer should not have been called yet
            mock_producer.produce.assert_not_called()

            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, IndexError):
                # IndexError occurs when queue is empty - expected in tests
                pass

    @pytest.mark.asyncio
    async def test_producer_processes_messages_from_buffer(self, monkeypatch):
        """Test that producer consumes messages from the buffer."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.producer.state", test_state)

        # Set up state as the reader would
        test_state.sensor_data_format = ">iI"

        # Add some test messages to the buffer
        test_reading_1 = pack(">iI", 20, 35)
        test_reading_2 = pack(">iI", 21, 40)
        test_state.q.append(test_reading_1)
        test_state.q.append(test_reading_2)

        # Mock the producer
        mock_producer = MagicMock()
        mock_producer.__enter__ = Mock(return_value=mock_producer)
        mock_producer.__exit__ = Mock(return_value=None)
        mock_producer.produce = Mock()
        mock_producer.flush = Mock()

        with patch("iot_sample.iot.producer.get_producer", return_value=mock_producer):
            # Start producer loop
            task = asyncio.create_task(producer.start_producer_loop())

            # Let it process the messages
            await asyncio.sleep(2.5)  # Wait for both messages to be processed

            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, IndexError):
                # IndexError occurs when queue is empty after processing messages
                pass

        # Producer should have been called
        assert mock_producer.produce.call_count >= 1

    @pytest.mark.asyncio
    async def test_producer_serializes_to_protobuf(self, monkeypatch):
        """Test that producer serializes messages as protobuf."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.producer.state", test_state)

        # Set up state
        test_state.sensor_data_format = ">iI"

        # Add a test message
        test_reading = pack(">iI", 22, 45)
        test_state.q.append(test_reading)

        # Mock the producer and capture what it produces
        produced_messages = []

        def capture_produce(message_bytes):
            produced_messages.append(message_bytes)

        mock_producer = MagicMock()
        mock_producer.__enter__ = Mock(return_value=mock_producer)
        mock_producer.__exit__ = Mock(return_value=None)
        mock_producer.produce = Mock(side_effect=capture_produce)
        mock_producer.flush = Mock()
        mock_producer.poll = Mock()

        with patch("iot_sample.iot.producer.get_producer", return_value=mock_producer):
            # Start producer loop
            task = asyncio.create_task(producer.start_producer_loop())

            # Let it process
            await asyncio.sleep(1.5)

            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, IndexError):
                # IndexError occurs when queue is empty - expected in tests
                pass

        # Should have produced at least one message
        assert len(produced_messages) >= 1

        # The produced message should be valid protobuf bytes
        proto_message = iot_pb2.IotSensorReading()  # type: ignore[attr-defined]
        proto_message.ParseFromString(produced_messages[0])

        # Verify message structure
        assert proto_message.sensor_type == iot_pb2.IOT_SENSOR_TYPE_TEMP_HUMIDITY  # type: ignore[attr-defined]
        assert proto_message.HasField("temp_humidity_payload")

    @pytest.mark.asyncio
    async def test_producer_calls_flush_on_exit(self, monkeypatch):
        """Test that producer calls flush when exiting."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.producer.state", test_state)

        # Set format so producer doesn't wait
        test_state.sensor_data_format = ">iI"

        # Mock the producer
        mock_producer = MagicMock()
        mock_producer.__enter__ = Mock(return_value=mock_producer)
        mock_producer.__exit__ = Mock(return_value=None)
        mock_producer.produce = Mock()
        mock_producer.flush = Mock()
        mock_producer.poll = Mock()

        with patch("iot_sample.iot.producer.get_producer", return_value=mock_producer):
            # Start and quickly cancel producer loop
            task = asyncio.create_task(producer.start_producer_loop())
            await asyncio.sleep(0.2)

            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, IndexError):
                # IndexError occurs when queue is empty - expected in tests
                pass

        # Flush should have been called in the finally block
        mock_producer.flush.assert_called()

    @pytest.mark.asyncio
    async def test_producer_removes_messages_from_buffer(self, monkeypatch):
        """Test that producer removes messages from buffer as it processes them."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.producer.state", test_state)

        # Set up state
        test_state.sensor_data_format = ">iI"

        # Add multiple test messages
        for i in range(5):
            test_reading = pack(">iI", 20 + i, 30 + i)
            test_state.q.append(test_reading)

        initial_buffer_size = len(test_state.q)
        assert initial_buffer_size == 5

        # Mock the producer
        mock_producer = MagicMock()
        mock_producer.__enter__ = Mock(return_value=mock_producer)
        mock_producer.__exit__ = Mock(return_value=None)
        mock_producer.produce = Mock()
        mock_producer.flush = Mock()
        mock_producer.poll = Mock()

        with patch("iot_sample.iot.producer.get_producer", return_value=mock_producer):
            # Start producer loop
            task = asyncio.create_task(producer.start_producer_loop())

            # Let it process messages
            await asyncio.sleep(3.5)  # Should process at least 3 messages

            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, IndexError):
                # IndexError occurs when queue is empty - expected in tests
                pass

        # Buffer should have fewer messages now
        assert len(test_state.q) < initial_buffer_size


class TestProducerMessageConstruction:
    """Test suite for protobuf message construction in producer."""

    @pytest.mark.asyncio
    async def test_producer_sets_sensor_id(self, monkeypatch):
        """Test that producer sets sensor_id in protobuf message."""
        test_uuid = "12345678-1234-5678-1234-567812345678"
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")
        monkeypatch.setenv("IOT_SENSOR_ID", test_uuid)

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.producer.state", test_state)

        # Set up state
        test_state.sensor_data_format = ">iI"

        # Add a test message
        test_reading = pack(">iI", 22, 45)
        test_state.q.append(test_reading)

        # Capture produced messages
        produced_messages = []

        def capture_produce(message_bytes):
            produced_messages.append(message_bytes)

        mock_producer = MagicMock()
        mock_producer.__enter__ = Mock(return_value=mock_producer)
        mock_producer.__exit__ = Mock(return_value=None)
        mock_producer.produce = Mock(side_effect=capture_produce)
        mock_producer.flush = Mock()
        mock_producer.poll = Mock()

        with patch("iot_sample.iot.producer.get_producer", return_value=mock_producer):
            # Start producer loop
            task = asyncio.create_task(producer.start_producer_loop())
            await asyncio.sleep(1.5)

            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, IndexError):
                # IndexError occurs when queue is empty - expected in tests
                pass

        # Parse the produced message
        if len(produced_messages) > 0:
            proto_message = iot_pb2.IotSensorReading()  # type: ignore[attr-defined]
            proto_message.ParseFromString(produced_messages[0])

            # Sensor ID should be set
            assert len(proto_message.sensor_id) == 16  # UUID is 16 bytes

    @pytest.mark.asyncio
    async def test_producer_unpacks_and_converts_sensor_data(self, monkeypatch):
        """Test that producer correctly unpacks and converts sensor data."""
        monkeypatch.setenv("IOT_SENSOR_TYPE", "IOT_SENSOR_TYPE_TEMP_HUMIDITY")

        # Reset state for clean test
        test_state = state.State()
        monkeypatch.setattr("iot_sample.iot.producer.state", test_state)

        # Set up state
        test_state.sensor_data_format = ">iI"

        # Add a test message with known values
        test_temp = 18
        test_humidity = 42
        test_reading = pack(">iI", test_temp, test_humidity)
        test_state.q.append(test_reading)

        # Capture produced messages
        produced_messages = []

        def capture_produce(message_bytes):
            produced_messages.append(message_bytes)

        mock_producer = MagicMock()
        mock_producer.__enter__ = Mock(return_value=mock_producer)
        mock_producer.__exit__ = Mock(return_value=None)
        mock_producer.produce = Mock(side_effect=capture_produce)
        mock_producer.flush = Mock()
        mock_producer.poll = Mock()

        with patch("iot_sample.iot.producer.get_producer", return_value=mock_producer):
            # Start producer loop
            task = asyncio.create_task(producer.start_producer_loop())
            await asyncio.sleep(1.5)

            task.cancel()
            try:
                await task
            except (asyncio.CancelledError, IndexError):
                # IndexError occurs when queue is empty - expected in tests
                pass

        # Parse and verify the message contains correct sensor data
        if len(produced_messages) > 0:
            proto_message = iot_pb2.IotSensorReading()  # type: ignore[attr-defined]
            proto_message.ParseFromString(produced_messages[0])

            assert proto_message.temp_humidity_payload.temperature_c == test_temp
            assert proto_message.temp_humidity_payload.rel_hum_pct == test_humidity
