import logging
from typing import Annotated
from typing import Union

from fastapi import APIRouter
from fastapi import Header
from fastapi import Path
from fastapi import Query

from distributed_locking_service.models.distributed_lock import DistributedLockModel
from distributed_locking_service.services.distributed_lock import DistributedLockService

router = APIRouter()

logger = logging.getLogger(__name__)


@router.post(
    "/distributed_lock/{lock_id}",
    response_model=DistributedLockModel,
    status_code=201,
    tags=["distributed-lock"],
)
async def post_distributed_lock(
    user_id: Annotated[Union[str, None], Header()],
    lock_id: str = Path(..., description="Distributed lock id"),
    is_write_exclusive: bool = Query(
        False,
        description="Bool that defines whether lock can be acquired by only a single write process",
    ),
) -> DistributedLockModel:
    dl_service: DistributedLockService = DistributedLockService(user_id)
    return await dl_service.create_lock(lock_id, is_write_exclusive)


@router.get(
    "/distributed_lock/{lock_id}",
    response_model=DistributedLockModel,
    status_code=200,
    tags=["distributed-lock"],
)
async def get_distributed_lock(
    user_id: Annotated[Union[str, None], Header()],
    lock_id: str = Path(..., description="Distributed lock id"),
) -> DistributedLockModel:
    dl_service: DistributedLockService = DistributedLockService(user_id)
    return await dl_service.get(lock_id)


@router.put(
    "/distributed_lock/{lock_id}/read-process/{process_id}",
    response_model=DistributedLockModel,
    status_code=200,
    tags=["distributed-lock"],
)
async def put_read_process(
    user_id: Annotated[Union[str, None], Header()],
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(..., description="Read process's id to add to distributed lock."),
    timeout: int = Query(60, description="Distributed lock id"),  # default timeout is 60 secs
) -> DistributedLockModel:
    dl_service: DistributedLockService = DistributedLockService(user_id)
    return await dl_service.add_read_process(lock_id, process_id, timeout)


@router.put(
    "/distributed_lock/{lock_id}/read-process/{process_id}/refresh",
    response_model=DistributedLockModel,
    status_code=200,
    tags=["distributed-lock"],
)
async def refresh_read_process(
    user_id: Annotated[Union[str, None], Header()],
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(..., description="Read process's id to add to distributed lock."),
    timeout: int = Query(60, description="Distributed lock id"),  # default timeout is 60 secs
) -> DistributedLockModel:
    dl_service: DistributedLockService = DistributedLockService(user_id)
    return await dl_service.add_read_process(lock_id, process_id, timeout, True)


@router.put(
    "/distributed_lock/{lock_id}/write-process/{process_id}",
    response_model=DistributedLockModel,
    status_code=200,
    tags=["distributed-lock"],
)
async def put_write_process(
    user_id: Annotated[Union[str, None], Header()],
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(..., description="Write process's id to add to distributed lock."),
    timeout: int = Query(60, description="Distributed lock id"),  # default timeout is 60 secs
) -> DistributedLockModel:
    dl_service: DistributedLockService = DistributedLockService(user_id)
    return await dl_service.add_write_process(lock_id, process_id, timeout)


@router.put(
    "/distributed_lock/{lock_id}/write-process/{process_id}/refresh",
    response_model=DistributedLockModel,
    status_code=200,
    tags=["distributed-lock"],
)
async def refresh_write_process(
    user_id: Annotated[Union[str, None], Header()],
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(..., description="Write process's id to add to distributed lock."),
    timeout: int = Query(60, description="Distributed lock id"),  # default timeout is 60 secs
) -> DistributedLockModel:
    dl_service: DistributedLockService = DistributedLockService(user_id)
    return await dl_service.add_write_process(lock_id, process_id, timeout, True)


@router.delete(
    "/distributed_lock/{lock_id}/read-process/{process_id}",
    response_model=DistributedLockModel,
    status_code=200,
    tags=["distributed-lock"],
)
async def del_read_process(
    user_id: Annotated[Union[str, None], Header()],
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(
        ..., description="Id of the read process to be deleted from the distributed lock."
    ),
) -> DistributedLockModel:
    dl_service: DistributedLockService = DistributedLockService(user_id)
    return await dl_service.del_read_process(lock_id, process_id)


@router.delete(
    "/distributed_lock/{lock_id}/write-process/{process_id}",
    response_model=DistributedLockModel,
    status_code=200,
    tags=["distributed-lock"],
)
async def del_write_process(
    user_id: Annotated[Union[str, None], Header()],
    lock_id: str = Path(..., description="Distributed lock id"),
    process_id: str = Path(
        ..., description="Id of the write process to be deleted from the distributed lock."
    ),
) -> DistributedLockModel:
    dl_service: DistributedLockService = DistributedLockService(user_id)
    return await dl_service.del_write_process(lock_id, process_id)
