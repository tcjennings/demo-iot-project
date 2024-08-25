"""Executable module for the application's server entrypoint."""

from asyncio import create_task
from contextlib import asynccontextmanager

import click
import uvicorn
from fastapi import FastAPI

from ..iot.producer import start_producer_loop
from ..iot.reader import start_sensor_reader_loop
from ..iot.state import state
from ..routers.internal import health
from ..routers.state import status


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start
    reader = create_task(start_sensor_reader_loop(), name="SensorReader")
    producer = create_task(start_producer_loop(), name="MessageProducer")
    state.tasks.append(reader)
    state.tasks.append(producer)
    yield
    # stop
    reader.cancel()


@click.command()
def main():
    # Create a FastAPI application using a custom lifespan context
    app = FastAPI(lifespan=lifespan)

    # Add router plugins to the FastAPI application
    app.include_router(health.router)
    app.include_router(status.router)

    # Run the FastAPI application with an ASGI web server
    uvicorn.run(app)


if __name__ == "__main__":
    main()
