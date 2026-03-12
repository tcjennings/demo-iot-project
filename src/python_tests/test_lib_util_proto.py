from struct import pack

import pytest

from iot_proto.iot.v1 import iot_pb2
from iot_sample.iot.sensors import emulated
from iot_sample.lib.utility import proto_tools


@pytest.mark.parametrize("name,value", iot_pb2.IotSensorType.items())  # type: ignore
def test_get_sensor_payload_descriptor(name, value):
    """Tests that a correct FieldDescriptor can be obtained from a message
    type based on the field number associated with a oneOf; and that a correct
    pydantic model is created from this descriptor.
    """
    try:
        field_descriptor = proto_tools.get_sensor_payload_descriptor(name)
        assert field_descriptor.number == value
    except (KeyError, SystemExit):
        # The IOT_SENSOR_TYPE_UNSPECIFIED enum is not associated with any oneOf
        # The code calls sys.exit(1) for this case
        assert value == 0
        return

    # Test the creation of a pydantic model from the proto message and the associated
    # fields
    model = proto_tools.model_from_proto_descriptor(field_descriptor.message_type)
    for field in field_descriptor.message_type.fields_by_name.keys():
        assert field in model.model_fields


@pytest.mark.parametrize(
    "sensor_class",
    [
        emulated.AirQualitySensor,
        emulated.TempHumiditySensor,
        emulated.LightSensor,
        emulated.OpenCloseSensor,
    ],
)
def test_emulated_sensor_payload(sensor_class):
    sensor = sensor_class()
    reading = pack(
        sensor.format_string,
        *[0, 0, 0, 0, 0, 0, 0, 0, 0, 0][: len(sensor.format_string)],
    )
    # proto_tools.proto_message_from_sensor_bytes(
    #     reading, sensor.format_string, field_descriptor, message_model
    # )
    assert reading
