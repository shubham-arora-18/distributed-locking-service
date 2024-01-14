from datetime import datetime

from pydantic import BaseModel
from pydantic.types import StrictStr


class HealthcheckResponse(BaseModel):
    message: StrictStr
    service_version: StrictStr
    commit_id: StrictStr
    time: datetime
