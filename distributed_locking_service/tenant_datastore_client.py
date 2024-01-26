import asyncio

from cachetools import TTLCache
from google.cloud import datastore

datastore_clients_cache: TTLCache = TTLCache(maxsize=100, ttl=600)
lock = asyncio.Lock()


class TenantDatastoreClient:
    @staticmethod
    async def get_datastore_client(user_id: str) -> datastore.Client:
        if user_id in datastore_clients_cache:
            return datastore_clients_cache[user_id]
        else:
            async with lock:
                if user_id in datastore_clients_cache:
                    return datastore_clients_cache[user_id]
                client = datastore.Client(namespace=user_id)
                datastore_clients_cache[user_id] = client
                return client
