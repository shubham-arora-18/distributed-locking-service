import copy
from datetime import datetime
from datetime import timezone

from pydantic import BaseModel


class Process(BaseModel):
    process_id: str
    lock_acquired_at: datetime
    timeout: int  # in seconds

    def __init__(self, **data):
        data_copy = copy.deepcopy(data)
        if not data_copy.get("lock_acquired_at"):
            data_copy["lock_acquired_at"] = datetime.now(timezone.utc)
        super().__init__(**data_copy)
