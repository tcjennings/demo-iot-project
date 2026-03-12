"""Implements a set of emulated Sensor classes for IOT hardware."""

import inspect
import sys

from . import IotSensor, fake


class TempHumiditySensor(IotSensor):
    format_string = "iI"
    sensor_type = "IOT_SENSOR_TYPE_TEMP_HUMIDITY"

    def get_measurement(self) -> tuple:
        """Returns a tuple of sensor readings, i.e., (temperature_c, rel_hum_pct)"""
        temperture_c = fake.pyint(min_value=0, max_value=22)
        rel_hum_pct = fake.pyint(min_value=20, max_value=45)
        return (temperture_c, rel_hum_pct)


class AirQualitySensor(IotSensor):
    """An Air Quality sensor.

    Versions
    --------
    1:
        - Carbon Dioxide as parts-per-million (safe maximum 1000)
        - Carbon Monoxide as parts-per-million (safe maximum 9)
        - Ozone as parts-per-billion (safe maximum 70)
    """

    format_string = "HHH"
    sensor_type = "IOT_SENSOR_TYPE_AIR_QUALITY"

    def get_measurement(self) -> tuple:
        """Returns a tuple of sensor readings, i.e., (co2_ppm, co_ppm, o3_ppb)"""
        co2_ppm = fake.pyint(min_value=700, max_value=1000)
        co_ppm = fake.pyint(min_value=2, max_value=5)
        o3_ppb = fake.pyint(min_value=40, max_value=60)
        return (co2_ppm, co_ppm, o3_ppb)


class OpenCloseSensor(IotSensor):
    """An open-close sensor, such as a reed switch or hall effect sensor.

    Versions
    --------
    1:
        - bit: 1 (closed), 0 (open)
    """

    format_string = "?"
    sensor_type = "IOT_SENSOR_TYPE_OPEN_CLOSE"

    def get_measurement(self) -> tuple:
        """Returns a tuple of sensor readings, i.e., (open/close,)"""
        open = fake.pybool(truth_probability=75)
        return (int(open),)


class LightSensor(IotSensor):
    """A light level sensor.

    Versions
    --------
    1:
        - measured lumens, approximate range [0, 3000]

    2:
        - measured color temperature in kelvin, approximate range [1700, 27000]
    """

    version = 2
    format_string = "HH"
    sensor_type = "IOT_SENSOR_TYPE_LIGHT"

    def get_measurement(self) -> tuple:
        lumens = fake.pyint(min_value=600, max_value=1500)
        color_temp_k = fake.pyint(min_value=2700, max_value=5400)
        return (lumens, color_temp_k)


def sensor_type_factory(sensor_type: str) -> type[IotSensor]:
    """Returns an `IotSensor` class for a sensor based on its type, by matching
    the ``sensor_type`` attribute of available classes in this module.
    """
    for _, o in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        if issubclass(o, IotSensor) and sensor_type == o.sensor_type:
            return o
    return IotSensor
