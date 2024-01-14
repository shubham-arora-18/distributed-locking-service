import asyncio

from cachetools import TTLCache
from google.cloud import datastore

datastore_clients_cache: TTLCache = TTLCache(maxsize=100, ttl=600)
lock = asyncio.Lock()


class TenantDatastoreClient:
    @staticmethod
    async def get_datastore_client(tenant_id: str) -> datastore.Client:
        if tenant_id in datastore_clients_cache:
            return datastore_clients_cache[tenant_id]
        else:
            async with lock:
                if tenant_id in datastore_clients_cache:
                    return datastore_clients_cache[tenant_id]
                client = datastore.Client(namespace=tenant_id)
                datastore_clients_cache[tenant_id] = client
                return client
