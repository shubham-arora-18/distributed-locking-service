import copy
from datetime import datetime
from datetime import timezone
from uuid import uuid4

from pydantic import BaseModel


class InvoptBaseModel(BaseModel):
    id: str
    created_at: datetime
    updated_at: datetime

    def __init__(self, **data):
        data_copy = copy.deepcopy(data)
        if "id" not in data_copy:
            data_copy["id"] = str(uuid4())
        if "updated_at" not in data_copy:
            data_copy["updated_at"] = datetime.now(timezone.utc)
        if "created_at" not in data_copy:
            data_copy["created_at"] = datetime.now(timezone.utc)
        super().__init__(**data_copy)

    def update_entity_updation_time(self):
        self.updated_at = datetime.now(timezone.utc)
