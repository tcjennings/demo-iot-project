from asyncio import sleep

import google.protobuf.message_factory as message_factory

from iot_proto.iot.v1 import iot_pb2

from ..lib.kafka.producer import get_producer
from ..lib.logging import logger
from ..lib.utility import proto_tools
from .settings import settings
from .state import state


async def start_producer_loop():
    # Get a message producer instance from an imported get_producer() function, which in
    # this case is a Kafka producer. This function should handle all the client setup,
    # bootstrapping, and configuration so that we do not need to further manipulate the
    # producer as it is returned.
    with get_producer() as producer:
        logger.info("Starting sensor read-eval-produce loop")

        # Set up a proto message for the sensor. This includes creating the
        # sensor reading message and the sensor payload message.
        # This is not expected to change during the lifetime of the application.
        sensor_reading = iot_pb2.IotSensorReading()  # type: ignore
        sensor_reading.sensor_id = settings.sensor_id.bytes
        sensor_reading.sensor_type = state.sensor_payload_descriptor.number

        # Produce sensor messages forever
        try:
            while True:
                if state.sensor_data_format is None:
                    # We cannot parse a message from the queue if the reader task has not
                    # yet registered the sensor data format
                    await sleep(1)
                    continue

                # take the oldest/leftmost message in the buffer deque
                message = state.q.popleft()

                # Unpack the message and create an instance of the reading's pydantic model
                message_object = proto_tools.get_sensor_reading_model(
                    message, state.sensor_data_format, state.message_model
                )

                # Create and populate a sensor_payload protobuf message with the current message
                # todo replace with proto_message_from_sensor_bytes
                sensor_payload = message_factory.GetMessageClass(
                    state.sensor_payload_descriptor.message_type
                )(**message_object.model_dump())

                # Using the getattr method, we can access variable or dynamic field names in the
                # sensor_reading protobuf message, then use the CopyFrom method to apply another
                # message to that field.
                getattr(sensor_reading, state.sensor_payload_descriptor.name).CopyFrom(
                    sensor_payload
                )

                # Now we are ready to publish the protobuf message for our current sensor reading.
                producer.produce(sensor_reading.SerializeToString())

                # Producer waits for new messages to be added to the buffer
                await sleep(1)
        finally:
            logger.info("Ending sensor read-eval-produce loop")
            producer.flush()
