import logging
import os

from auth.custom_exceptions import CustomException
from fastapi import FastAPI
from fastapi import exceptions
from fastapi import status
from fastapi.responses import JSONResponse
from fastapi_versioning import VersionedFastAPI

from distributed_locking_service import __project_id__
from distributed_locking_service import __version__
from distributed_locking_service.custom_logging import configure_logging
from distributed_locking_service.routers import distributed_lock
from distributed_locking_service.routers import health

os.environ["TZ"] = "UTC"
configure_logging()

app = FastAPI(title=f"Model Registry Service: {__project_id__}", version=__version__)

logger = logging.getLogger(__name__)


# exception_handlers
@app.exception_handler(CustomException)
async def custom_exception_handler(request, exc):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"Error message": str(exc)},
    )


@app.exception_handler(exceptions.RequestValidationError)
async def request_validation_exception_handler(request, exc):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"Error message": str(exc)},
    )


@app.exception_handler(Exception)
async def base_exception_handler(request, exc):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"Error message": str(exc)},
    )


# routers
app.include_router(health.router)
app.include_router(distributed_lock.router)

handlers_to_apply = {}
for ex, func in app.exception_handlers.items():
    handlers_to_apply[ex] = func

app = VersionedFastAPI(app, version_format="{major}", prefix_format="/v{major}")

for sub_app in app.routes:
    if hasattr(sub_app.app, "add_exception_handler"):  # type: ignore
        for ex, func in handlers_to_apply.items():
            sub_app.app.add_exception_handler(ex, func)  # type: ignore


# import uvicorn
#
# os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"
# os.environ["CLOUDSDK_CORE_PROJECT"] = "test"
# # os.environ["GOOGLE_CLOUD_PROJECT"] = "qp-sandbox-inventory-4f59"
# # os.environ["GOOGLE_CLOUD_PROJECT"] = "at-invopt-lle-lle1-ae8c"
# uvicorn.run(app, host="0.0.0.0", port=9090)
