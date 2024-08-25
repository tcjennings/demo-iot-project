from fastapi import APIRouter

# to decouple the router from the app, this state should be available
# via middleware or dependency injection instead
from ...iot.state import state

router = APIRouter()


@router.get("/health", tags=["internal", "health"])
async def get_health():
    """Checks the health status of the application. Checks any running tasks
    in the application's state object, where a `done` task indicates a broken
    application instance where an exception may be present.
    """
    server_ok = True
    health_response = {}
    for task in state.tasks:
        task_response = {"task_running": True, "task_exception": None}

        if task.done():
            server_ok = False
            task_response["task_running"] = False
            task_response["task_exception"] = task.exception()

        health_response[task.get_name()] = task_response

    health_response["server_status":server_ok]

    # Should return code 500 if not server_ok
    return health_response
