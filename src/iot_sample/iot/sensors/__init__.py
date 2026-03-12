"""Module implementing emulated IOT sensors, which all operate the same way.

Each IotSensor is expected to emit payload values in packed binary messages
using network byte order. Each sensor defines the order and type of the values
that are packed into its payload, and this payload format is used to define
the protobuf messages associated with such a sensor.

These emulated sensors do not implement any internal clock; i.e., they are not
asynchronous processes that produce measurements over time. Instead, unlike a
hardware sensor, they will only send a message when asked for one.
"""

import abc
from struct import pack

from faker import Faker

fake = Faker()
"""An instance of a Faker to use in peer modules."""


class IotSensor(abc.ABC):
    byte_order = ">"  # big-endian
    format_string = ""  # format string used by struct.pack
    sensor_type = "IOT_SENSOR_TYPE_UNSPECIFIED"  # Name of the sensor type used in the matching protobuf message
    version = 1  # version number for the sensor

    def __call__(self):
        """When called, a sensor must emit its message in a packed binary format"""
        return pack(f"{self.byte_order}{self.format_string}", *self.get_measurement())

    @abc.abstractmethod
    def get_measurement(self) -> tuple:
        """Generate a measurement for the sensor to emit as its payload.

        This must return a sequence of values that are compatible with the types defined
        for the sensor's `format_string`, e.g., for the format string `iI` this method
        must produce a sequence of length 2 containing an `unsigned int` and a `signed int`.
        """
        raise NotImplementedError
