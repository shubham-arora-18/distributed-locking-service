import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Path
from fastapi import Query
from fastapi import Request

from distributed_locking_service.auth.auth_bearer import JWTBearer
from distributed_locking_service.auth.auth_bearer import (
    fetch_tenant_id_from_jwt_payload,
)
from distributed_locking_service.models.distributed_lock import DistributedLockModel
from distributed_locking_service.services.distributed_lock import DistributedLockService

router = APIRouter()

logger = logging.getLogger(__name__)

jwt_bearer_dependency = Depends(JWTBearer())


@router.post(
    "/distributed_lock/{lock_id}",
    response_model=DistributedLockModel,
    dependencies=[jwt_bearer_dependency],
    status_code=201,
    tags=["distributed-lock"],
)
async def post_distributed_lock(
    request: Request,
    lock_id: str = Path(..., description="Distributed lock id"),
    is_write_exclusive: bool = Query(
        False,
        description="Bool that defines whether lock can be acquired by only a single write process",
    ),
) -> DistributedLockModel:
    tenant_id = fetch_tenant_id_from_jwt_payload(request)
    dl_service: DistributedLockService = DistributedLockService(tenant_id)
    return await dl_service.create_lock(lock_id, is_write_exclusive)


@router.get(
    "/distributed_lock/{lock_id}",
    response_model=DistributedLockModel,
    dependencies=[jwt_bearer_dependency],
    status_code=200,
    tags=["distributed-lock"],
)
async def get_distributed_lock(
    request: Request, lock_id: str = Path(..., description="Distributed lock id")
) -> DistributedLockModel:
    tenant_id = fetch_tenant_id_from_jwt_payload(request)
    dl_service: DistributedLockService = DistributedLockService(tenant_id)
    return await dl_service.get(lock_id)


@router.put(
    "/distributed_lock/{lock_id}/read-process/{process_id}",
    response_model=DistributedLockModel,
    dependencies=[jwt_bearer_dependency],
    status_code=200,
    tags=["distributed-lock"],
)
async def put_read_process(
    request: Request,
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(..., description="Read process's id to add to distributed lock."),
    timeout: int = Query(60, description="Distributed lock id"),  # default timeout is 60 secs
) -> DistributedLockModel:
    tenant_id = fetch_tenant_id_from_jwt_payload(request)
    dl_service: DistributedLockService = DistributedLockService(tenant_id)
    return await dl_service.add_read_process(lock_id, process_id, timeout)


@router.put(
    "/distributed_lock/{lock_id}/write-process/{process_id}",
    response_model=DistributedLockModel,
    dependencies=[jwt_bearer_dependency],
    status_code=200,
    tags=["distributed-lock"],
)
async def put_write_process(
    request: Request,
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(..., description="Write process's id to add to distributed lock."),
    timeout: int = Query(60, description="Distributed lock id"),  # default timeout is 60 secs
) -> DistributedLockModel:
    tenant_id = fetch_tenant_id_from_jwt_payload(request)
    dl_service: DistributedLockService = DistributedLockService(tenant_id)
    return await dl_service.add_write_process(lock_id, process_id, timeout)


@router.delete(
    "/distributed_lock/{lock_id}/read-process/{process_id}",
    response_model=DistributedLockModel,
    dependencies=[jwt_bearer_dependency],
    status_code=200,
    tags=["distributed-lock"],
)
async def del_read_process(
    request: Request,
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(
        ..., description="Id of the read process to be deleted from the distributed lock."
    ),
) -> DistributedLockModel:
    tenant_id = fetch_tenant_id_from_jwt_payload(request)
    dl_service: DistributedLockService = DistributedLockService(tenant_id)
    return await dl_service.del_read_process(lock_id, process_id)


@router.delete(
    "/distributed_lock/{lock_id}/write-process/{process_id}",
    response_model=DistributedLockModel,
    dependencies=[jwt_bearer_dependency],
    status_code=200,
    tags=["distributed-lock"],
)
async def del_write_process(
    request: Request,
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(
        ..., description="Id of the write process to be deleted from the distributed lock."
    ),
) -> DistributedLockModel:
    tenant_id = fetch_tenant_id_from_jwt_payload(request)
    dl_service: DistributedLockService = DistributedLockService(tenant_id)
    return await dl_service.del_write_process(lock_id, process_id)
