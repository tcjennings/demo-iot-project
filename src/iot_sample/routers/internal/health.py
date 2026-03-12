from typing import TypedDict

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# TODO: to decouple the router from the app, this state should be available
# via middleware or dependency injection instead
from ...iot.state import state

router = APIRouter()


class TaskResponse(TypedDict):
    task_running: bool
    task_exception: str | None


@router.get("/health", tags=["internal", "health"])
async def get_health():
    """Checks the health status of the application. Checks any running tasks
    in the application's state object, where a `done` task indicates a broken
    application instance where an exception may be present.
    """
    server_ok = True
    health_response = {}
    for task in state.tasks:
        task_response: TaskResponse = {"task_running": True, "task_exception": None}

        if task.done():
            server_ok = False
            task_response["task_running"] = False
            task_response["task_exception"] = str(task.exception())

        health_response[task.get_name()] = task_response

    health_response["server_status"] = server_ok

    # Should return code 500 if not server_ok
    if not server_ok:
        raise HTTPException(status_code=500, detail=health_response)
    else:
        return JSONResponse(health_response)
