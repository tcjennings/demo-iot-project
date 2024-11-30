from asyncio import sleep

from ..lib.logging import logger
from .sensors import emulated
from .settings import settings
from .state import state


async def start_sensor_reader_loop():
    """The reader loop reads the output from a sensor interface and adds the raw bytes to a
    state buffer.
    """

    # Create an instance of an emulated IOT sensor
    iot_sensor = (
        emulated.TempHumiditySensor()
    )  # this should be dynamic based on the sensor-type

    # Update application state with the sensor's data format string
    state.sensor_data_format = f"{iot_sensor.byte_order}{iot_sensor.format_string}"

    logger.info("Starting sensor read-buffer loop")

    # Read sensor messages into the state buffer forever
    try:
        while True:
            reading = iot_sensor()
            state.q.append(reading)

            # Sensors may operate at any arbitrary frequency, default is 1 hz
            await sleep(1 / settings.frequency)
    finally:
        logger.info("Ending sensor read-buffer loop")
