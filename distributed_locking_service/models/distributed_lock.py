import copy
from typing import List

from distributed_locking_service.constants import LockState
from distributed_locking_service.models.base import InvoptBaseModel
from distributed_locking_service.models.process import Process


class DistributedLockModel(InvoptBaseModel):
    lock_id: str
    read_process_list: List[Process] = []
    write_process_list: List[Process] = []
    is_write_exclusive: bool = False
    current_state: LockState = LockState.FREE

    def __init__(self, **data):
        data_copy = copy.deepcopy(data)
        super().__init__(**data_copy)
