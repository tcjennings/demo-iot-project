"""Module describing an application state object. An instance of this state object
should be created at application start up and its class variables be accessible by
multiple threads as necessary for different parts of the application.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

from google.protobuf.descriptor import FieldDescriptor
from pydantic import BaseModel

from ..lib.utility import proto_tools
from .settings import settings

if TYPE_CHECKING:
    from fastapi import FastAPI

    from ..lib.kafka.stats import RdKafkaStats


class State:
    q: deque
    sensor_payload_descriptor: FieldDescriptor
    message_model: BaseModel
    sensor_data_format: str | None
    tasks: set
    statistics: RdKafkaStats | dict
    fastapi: FastAPI

    def __init__(self):
        self.q = deque(maxlen=(settings.buffer_time_sec * settings.frequency))
        # deque is a rolling buffer of sensor readings that can be read or consumed
        # by other parts of the application. The buffer is sufficient to hold a number
        # of readings determined by the buffer length in time and the frequency of readings

        self.sensor_payload_descriptor = proto_tools.get_sensor_payload_descriptor(
            settings.sensor_type
        )
        self.message_model = proto_tools.model_from_proto_descriptor(
            self.sensor_payload_descriptor.message_type
        )
        self.sensor_data_format = None
        self.tasks = set()
        self.statistics = {}


state = State()
"""A global state instance"""
