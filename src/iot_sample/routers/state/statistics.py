from functools import partial

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

from ...iot.state import state

router = APIRouter()


@router.get("/statistics")
@router.get("/metrics")
async def get_metrics():
    """Present statistics snapshot from application state."""
    match state.statistics:
        case dict():
            stats_callable = partial(JSONResponse, state.statistics)
        case _:
            stats_callable = partial(
                JSONResponse, state.statistics.model_dump(exclude_unset=True)
            )

    return stats_callable()


@router.get("/openmetrics")
async def get_openmetrics() -> Response:
    """NOT YET IMPLEMENTED: Present statistics snapshot from application state in OpenMetrics format."""
    metrics_body = ""
    metrics_body += "# EOF\n"

    return Response(
        content=metrics_body,
        media_type="application/openmetrics-text; version=1.0.0; charset=utf-8",
    )
