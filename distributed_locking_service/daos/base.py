import logging
from typing import Generic
from typing import Optional
from typing import Type
from typing import TypeVar

from google.cloud import datastore

from distributed_locking_service.exceptions import MissingDataException
from distributed_locking_service.models.base import InvoptBaseModel
from distributed_locking_service.tenant_datastore_client import TenantDatastoreClient

model_T = TypeVar("model_T", bound=InvoptBaseModel)

logger = logging.getLogger()


class InvoptBaseDAO(Generic[model_T]):
    def __init__(self, kind: str, __model_return_type__: Type[model_T], tenant_id: str):
        self.tenant_id = tenant_id
        self.__kind__ = kind
        self.__model_return_type__ = __model_return_type__

    async def create(self, datastore_entity: model_T) -> model_T:
        db_client = await TenantDatastoreClient.get_datastore_client(self.tenant_id)
        key = db_client.key(self.__kind__, datastore_entity.id)
        entity = datastore.Entity(key=key)
        entity_dict = datastore_entity.dict()
        entity.update(entity_dict)
        db_client.put(entity)
        return datastore_entity

    async def get(self, id: str) -> model_T:
        db_client = await TenantDatastoreClient.get_datastore_client(self.tenant_id)
        key = db_client.key(self.__kind__, str(id))
        entity = db_client.get(key)
        if entity is None:
            raise MissingDataException(
                f"{self.__model_return_type__.__name__} with id: {id} not found."
            )
        return self.__model_return_type__(**entity)

    async def update(self, updated_entity: model_T) -> model_T:
        updated_entity.update_entity_updation_time()
        return await self.create(updated_entity)

    async def get_query(
        self,
        filters: list[tuple],
        limit: Optional[int] = None,
        order_property: Optional[str] = None,
    ) -> list[model_T]:
        db_client = await TenantDatastoreClient.get_datastore_client(self.tenant_id)
        query = db_client.query(kind=self.__kind__)
        if order_property:
            query.order = [order_property]
        for column, operator, value in filters:
            query.add_filter(column, operator, value)

        results = list(query.fetch(limit=limit))
        model_instances = [self.__model_return_type__(**entity) for entity in results]
        return model_instances
