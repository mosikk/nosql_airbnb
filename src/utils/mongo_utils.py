import os
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

mongo_client: AsyncIOMotorClient = None


async def get_db_collection() -> AsyncIOMotorCollection:
    mongo_uri = os.getenv('MONGO_URI')
    mongo_db = os.getenv('MONGO_DB')
    mongo_clients_collection = os.getenv('MONGO_CLIENTS_COLLECTION')
    mongo_rooms_collection = os.getenv('MONGO_ROOMS_COLLECTION')
    mongo_bookings_collection = os.getenv('MONGO_BOOKINGS_COLLECTION')

    return mongo_client.get_database(mongo_db).get_collection(mongo_collection)


async def connect_and_init_mongo():
    global mongo_client
    mongo_uri = os.getenv('MONGO_URI')
    mongo_db = os.getenv('MONGO_DB')
    mongo_clients_collection = os.getenv('MONGO_CLIENTS_COLLECTION')
    mongo_rooms_collection = os.getenv('MONGO_ROOMS_COLLECTION')
    mongo_bookings_collection = os.getenv('MONGO_BOOKINGS_COLLECTION')

    try:
        mongo_client = AsyncIOMotorClient(mongo_uri)
        await mongo_client.server_info()
        print(f'Connected to mongo with uri {mongo_uri}')
        if mongo_db not in await mongo_client.list_database_names():
            await mongo_client \
                .get_database(mongo_db) \
                .create_collection(mongo_clients_collection)
            print(f'Database {mongo_db} created')
            print(f'Collection {mongo_clients_collection} created')

            await mongo_client \
                .get_database(mongo_db) \
                .create_collection(mongo_rooms_collection)
            print(f'Collection {mongo_rooms_collection} created')

            await mongo_client \
                .get_database(mongo_db) \
                .create_collection(mongo_bookings_collection)
            print(f'Collection {mongo_bookings_collection} created')

    except Exception as ex:
        print(f'Cant connect to mongo: {ex}')


def close_mongo_connect():
    global mongo_client
    if mongo_client is None:
        return
    mongo_client.close()


def filter_by_id(id: str) -> dict:
    return {'_id': ObjectId(id)}
