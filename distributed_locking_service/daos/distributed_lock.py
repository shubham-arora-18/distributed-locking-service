from typing import Any

from distributed_locking_service.daos.base import InvoptBaseDAO
from distributed_locking_service.exceptions import InternalServerException
from distributed_locking_service.exceptions import MissingDataException
from distributed_locking_service.models.distributed_lock import DistributedLockModel


class DistributedLockDAO(InvoptBaseDAO):
    def __init__(self, tenant_id: str):
        super().__init__("distributed_lock", DistributedLockModel, tenant_id)

    async def get(self, lock_id: str) -> DistributedLockModel:
        filters: list[tuple[Any, ...]] = [
            ("lock_id", "=", lock_id),
        ]
        lock_list = await super().get_query(filters)
        if len(lock_list) == 0:
            raise MissingDataException(f"DistributedLock with lock_id: {lock_id} not found.")
        elif len(lock_list) > 1:
            raise InternalServerException(
                f"Multiple entries with the lock_id: {lock_id} present. " f"Please contact admin."
            )
        return lock_list[0]
