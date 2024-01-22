import copy
import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional

from fastapi import status

from distributed_locking_service.constants import LockState
from distributed_locking_service.daos.distributed_lock import DistributedLockDAO
from distributed_locking_service.exceptions import CustomException
from distributed_locking_service.exceptions import InvalidInputException
from distributed_locking_service.exceptions import MissingDataException
from distributed_locking_service.models.distributed_lock import DistributedLockModel
from distributed_locking_service.models.process import Process
from distributed_locking_service.services.base import InvoptBaseService
from distributed_locking_service.tenant_datastore_client import TenantDatastoreClient

logger = logging.getLogger(__name__)


class DistributedLockService(InvoptBaseService):
    def __init__(self, tenant_id):
        super().__init__(DistributedLockDAO(tenant_id), DistributedLockModel)

    async def create_lock(self, lock_id: str, is_write_exclusive: bool) -> DistributedLockModel:
        db_client = await TenantDatastoreClient.get_datastore_client(self.dao_obj.tenant_id)
        with db_client.transaction():
            try:
                await super().get(lock_id)
                raise InvalidInputException(
                    f"Different Lock with id:{lock_id} already exists" f". Please try again."
                )
            except MissingDataException:
                return await super().create(lock_id=lock_id, is_write_exclusive=is_write_exclusive)

    async def get(self, lock_id: str) -> DistributedLockModel:
        db_client = await TenantDatastoreClient.get_datastore_client(self.dao_obj.tenant_id)
        with db_client.transaction():
            return await self.refresh_lock(await super().get(lock_id))

    async def add_read_process(
        self, lock_id: str, read_process_id: str, timeout: int, refresh: bool = False
    ) -> DistributedLockModel:
        db_client = await TenantDatastoreClient.get_datastore_client(self.dao_obj.tenant_id)
        with db_client.transaction():
            lock: DistributedLockModel = await super().get(
                lock_id
            )  # for the transaction to work right, it is important
            # that we first get and then update the entity
            lock = await self.refresh_lock(lock)
            if lock.current_state == LockState.WRITE:
                raise CustomException(
                    f"The lock with lock_id:{lock_id} is currently in WRITE state. Please "
                    f"wait for the lock to return to FREE or READ state. "
                    f"Current lock state: {lock.json()}",
                    status.HTTP_409_CONFLICT,
                )
            elif lock.current_state == LockState.FREE:
                lock.current_state = LockState.READ
                lock.read_process_list.append(Process(process_id=read_process_id, timeout=timeout))
                await super().update(lock)
            else:
                try:
                    matching_process: Optional[Process] = next(
                        rp for rp in lock.read_process_list if rp.process_id == read_process_id
                    )
                except StopIteration:
                    matching_process = None

                if matching_process is not None:
                    if not refresh:
                        raise CustomException(
                            f"Process id {read_process_id} already present in the lock. "
                            f"Current lock state: {lock.json()}",
                            status.HTTP_406_NOT_ACCEPTABLE,
                        )
                    else:
                        lock.read_process_list.remove(matching_process)
                lock.read_process_list.append(Process(process_id=read_process_id, timeout=timeout))
                await super().update(lock)

        return lock

    async def add_write_process(
        self, lock_id: str, write_process_id: str, timeout: int, refresh: bool = False
    ) -> DistributedLockModel:
        db_client = await TenantDatastoreClient.get_datastore_client(self.dao_obj.tenant_id)
        with db_client.transaction():
            lock: DistributedLockModel = await super().get(lock_id)
            lock = await self.refresh_lock(lock)
            if lock.current_state == LockState.READ:
                raise CustomException(
                    f"The lock with lock_id:{lock_id} is currently in READ state. Please "
                    f"wait for the lock to return to FREE or READ state. "
                    f"Current lock state: {lock.json()}",
                    status.HTTP_409_CONFLICT,
                )
            elif lock.current_state == LockState.FREE:
                lock.current_state = LockState.WRITE
                lock.write_process_list.append(
                    Process(process_id=write_process_id, timeout=timeout)
                )
                await super().update(lock)
            else:
                try:
                    matching_process: Optional[Process] = next(
                        wp for wp in lock.write_process_list if wp.process_id == write_process_id
                    )
                except StopIteration:
                    matching_process = None

                if matching_process is not None:
                    if not refresh:
                        raise CustomException(
                            f"Process id {write_process_id} already present in the lock. "
                            f"Current lock state: {lock.json()}",
                            status.HTTP_406_NOT_ACCEPTABLE,
                        )
                    else:
                        lock.write_process_list.remove(matching_process)

                if lock.is_write_exclusive:
                    raise CustomException(
                        f"The lock is write exclusive. It can only hold one write process"
                        f" at a time. Current lock state: {lock.json()}",
                        status.HTTP_409_CONFLICT,
                    )
                lock.write_process_list.append(
                    Process(process_id=write_process_id, timeout=timeout)
                )
                await super().update(lock)

        return lock

    async def del_read_process(self, lock_id: str, read_process_id: str) -> DistributedLockModel:
        db_client = await TenantDatastoreClient.get_datastore_client(self.dao_obj.tenant_id)
        with db_client.transaction():
            lock: DistributedLockModel = await super().get(lock_id)
            lock = await self.refresh_lock(lock)
            if lock.current_state == LockState.FREE:
                raise InvalidInputException(
                    f"The lock is already in FREE state. Current lock state: {lock.json()}"
                )
            elif lock.current_state == LockState.WRITE:
                raise InvalidInputException(
                    f"The lock is currently in WRITE state. Current lock state: {lock.json()}"
                )
            else:
                try:
                    selected_read_process = next(
                        rp for rp in lock.read_process_list if rp.process_id == read_process_id
                    )
                except StopIteration:
                    raise InvalidInputException(
                        f"The process is not present in lock's read list. "
                        f"Current lock state: {lock.json()}"
                    )
                lock.read_process_list.remove(selected_read_process)
                if len(lock.read_process_list) == 0:
                    lock.current_state = LockState.FREE
                await super().update(lock)

        return lock

    async def del_write_process(self, lock_id: str, write_process_id: str) -> DistributedLockModel:
        db_client = await TenantDatastoreClient.get_datastore_client(self.dao_obj.tenant_id)
        with db_client.transaction():
            lock: DistributedLockModel = await super().get(lock_id)
            lock = await self.refresh_lock(lock)
            if lock.current_state == LockState.FREE:
                raise InvalidInputException(
                    f"The lock is already in FREE state. Current lock state: {lock.json()}"
                )
            elif lock.current_state == LockState.READ:
                raise InvalidInputException(
                    f"The lock is currently in READ state. Current lock state: {lock.json()}"
                )
            else:
                try:
                    selected_write_process = next(
                        wp for wp in lock.write_process_list if wp.process_id == write_process_id
                    )
                except StopIteration:
                    raise InvalidInputException(
                        f"The process is not present in lock's write list. "
                        f"Current lock state: {lock.json()}"
                    )
                lock.write_process_list.remove(selected_write_process)
                if len(lock.write_process_list) == 0:
                    lock.current_state = LockState.FREE
                await super().update(lock)

        return lock

    async def refresh_lock(self, lock: DistributedLockModel) -> DistributedLockModel:
        lock_copy = copy.deepcopy(lock)
        current_time = datetime.now(timezone.utc)
        lock.write_process_list = [
            process
            for process in lock.write_process_list
            if current_time < process.lock_acquired_at + timedelta(seconds=process.timeout)
        ]
        lock.read_process_list = [
            process
            for process in lock.read_process_list
            if current_time < process.lock_acquired_at + timedelta(seconds=process.timeout)
        ]

        if len(lock.read_process_list) == 0 and len(lock.write_process_list) == 0:
            lock.current_state = LockState.FREE
        elif len(lock.read_process_list) > 0:
            lock.current_state = LockState.READ
        else:
            lock.current_state = LockState.WRITE

        if lock_copy != lock:
            logger.info(f"Refreshing lock state from :{lock_copy.json()} to {lock.json()}")
            return await super().update(lock)
        else:
            logger.info("Lock refreshing not needed.")
            return lock_copy
