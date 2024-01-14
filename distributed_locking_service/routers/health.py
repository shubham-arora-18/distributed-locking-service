import logging
import os
from datetime import datetime
from datetime import timezone

from fastapi import APIRouter

from distributed_locking_service import __version__
from distributed_locking_service.models.health import HealthcheckResponse

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/healthcheck", response_model=HealthcheckResponse, tags=["health"])
def healthcheck() -> HealthcheckResponse:
    message = "healthy"

    logger.info(message)
    return HealthcheckResponse(
        message=message,
        service_version=__version__,
        commit_id=os.environ.get("COMMIT_ID", "No commit id found!"),
        time=datetime.now(timezone.utc),
    )
