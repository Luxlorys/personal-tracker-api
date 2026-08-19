"""Infrastructure endpoint.

Deliberately bypasses the use case layer: it reports on the process and its
connections, which is not a business capability.
"""

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.drivers.rest.dependencies import RedisDependency, SessionDependency

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health(session: SessionDependency, redis: RedisDependency) -> JSONResponse:
    checks = {"database": False, "cache": False}
    try:
        await session.execute(text("SELECT 1"))
        checks["database"] = True
    except Exception:  # noqa: BLE001
        checks["database"] = False
    try:
        checks["cache"] = bool(await redis.ping())
    except Exception:  # noqa: BLE001
        checks["cache"] = False

    healthy = all(checks.values())
    return JSONResponse(
        status_code=status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"status": "ok" if healthy else "degraded", **checks},
    )
