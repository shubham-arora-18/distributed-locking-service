from typing import Generic
from typing import Type
from typing import TypeVar

from distributed_locking_service.daos.base import InvoptBaseDAO
from distributed_locking_service.models.base import InvoptBaseModel

dao_T = TypeVar("dao_T", bound=InvoptBaseDAO)
model_T = TypeVar("model_T", bound=InvoptBaseModel)


class InvoptBaseService(Generic[dao_T, model_T]):
    def __init__(self, dao_obj: dao_T, model_obj_type: Type[model_T]):
        self.dao_obj = dao_obj
        self.__model_obj_type__ = model_obj_type

    async def create(self, **data) -> model_T:
        model_obj: model_T = self.__model_obj_type__(**data)
        return await self.dao_obj.create(model_obj)

    async def get(self, entity_id: str) -> model_T:
        return await self.dao_obj.get(entity_id)

    async def update(self, updated_entity: model_T) -> model_T:
        return await self.dao_obj.update(updated_entity)
