import os

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

from utils.mongo_utils import filter_by_id, filter_by_name
from models.booking import Booking, UpdateBooking
from models.client import Client, UpdateClient
from models.room import Room, UpdateRoom


mongo_client: AsyncIOMotorClient = None


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
            await mongo_client.get_database(mongo_db).create_collection(mongo_clients_collection)
            print(f'Collection {mongo_clients_collection} created', flush=True)

            await mongo_client.get_database(mongo_db).create_collection(mongo_rooms_collection)
            print(f'Collection {mongo_rooms_collection} created', flush=True)

            await mongo_client.get_database(mongo_db).create_collection(mongo_bookings_collection)
            print(f'Collection {mongo_bookings_collection} created', flush=True)

            mongo_clients_collection = mongo_client.get_database(mongo_db).get_collection(mongo_clients_collection)
            mongo_rooms_collection = mongo_client.get_database(mongo_db).get_collection(mongo_rooms_collection)
            mongo_bookings_collection = mongo_client.get_database(mongo_db).get_collection(mongo_bookings_collection)

            print(f'Database {mongo_db} created', flush=True)

    except Exception as ex:
        print(f'Cant connect to mongo: {ex}', flush=True)


def close_mongo_connect():
    global mongo_client
    if mongo_client is None:
        return
    mongo_client.close()


class MongoRepository:
    def __init__(self):
        mongo_db = os.getenv('MONGO_DB')
        mongo_clients_collection = os.getenv('MONGO_CLIENTS_COLLECTION')
        mongo_rooms_collection = os.getenv('MONGO_ROOMS_COLLECTION')
        mongo_bookings_collection = os.getenv('MONGO_BOOKINGS_COLLECTION')

        self._mongo_clients_collection = mongo_client.get_database(mongo_db).get_collection(mongo_clients_collection)
        self._mongo_rooms_collection = mongo_client.get_database(mongo_db).get_collection(mongo_rooms_collection)
        self._mongo_bookings_collection = mongo_client.get_database(mongo_db).get_collection(mongo_bookings_collection)
    

    async def __del__(self):
        await self.close_connection()

    
    async def create_client(self, client: UpdateClient) -> str:
        insert_result = await self._mongo_clients_collection.insert_one(dict(client))
        return str(insert_result.inserted_id)
    

    async def get_client_by_id(self, client_id: str) -> Client | None:
        client = await self._mongo_clients_collection.find_one(filter_by_id(client_id))
        return Client.Map(client)


    async def get_client_by_name(self, client_name: str) -> Client | None:
        client = await self._mongo_clients_collection.find_one(filter_by_name(client_name))
        return Client.Map(client)
    

    async def create_room(self, room: UpdateClient) -> str:
        insert_result = await self._mongo_rooms_collection.insert_one(dict(room))
        return str(insert_result.inserted_id)
    

    async def get_room_by_id(self, room_id: str) -> Room | None:
        room = await self._mongo_rooms_collection.find_one(filter_by_id(room_id))
        return Room.Map(room)


    async def book_room(self, booking: UpdateBooking) -> str:
        insert_result = await self._mongo_bookings_collection.insert_one(dict(booking))
        return str(insert_result.inserted_id)
    

    async def pay_booking(self, booking_id: str) -> Booking | None:
        cur_booking = Booking.Map(await self._mongo_bookings_collection.find_one(filter_by_id(booking_id)))
        if cur_booking.is_paid == True:
            print(f'Booking {booking_id} is already paid', flush=True)
            return None
        new_booking = Booking(id=cur_booking.id, client_id=cur_booking.client_id, room_id=cur_booking.room_id, is_paid=True)
        await self._mongo_bookings_collection.find_one_and_replace(filter_by_id(booking_id), dict(new_booking))
        return new_booking


    async def get_booking_by_id(self, booking_id: str) -> Booking | None:
        booking = await self._mongo_bookings_collection.find_one(filter_by_id(booking_id))
        return Booking.Map(booking)


    @staticmethod
    def get_instance():
        return MongoRepository()
