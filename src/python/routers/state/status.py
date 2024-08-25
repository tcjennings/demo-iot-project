from fastapi import APIRouter, WebSocket

from ...iot.state import state
from ...lib.utility import proto_tools

router = APIRouter()


@router.websocket("/status")
async def get_status(websocket: WebSocket):
    """A websocket endpoint for tracking the current status of the measured sensor supported
    by the application.
    """
    await websocket.accept()
    while True:
        latest_value = {}

        if state.sensor_data_format is None:
            # Sensor data format has not been registered in application state yet
            await websocket.send_json(latest_value)

        # read the latest sensor value from the application's state buffer
        elif len(state.q) > 0:
            latest_value = proto_tools.get_sensor_reading_model(
                state.q[-1], state.sensor_data_format, state.message_model
            )
            await websocket.send_json(data=latest_value.model_dump_json())
