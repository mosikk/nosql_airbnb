import os

from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from utils.mongo_utils import get_db_collection, filter_by_id, filter_by_booking_id
from models.booking import Booking, UpdateBooking
from models.client import Client, UpdateClient
from models.room import Room, UpdateRoom


class MongoRepository:
    mongo_client: AsyncIOMotorCollection

    def __init__(self, db_collection: AsyncIOMotorCollection):
        mongo_db = os.getenv('MONGO_DB')
        mongo_clients_collection = os.getenv('MONGO_CLIENTS_COLLECTION')
        mongo_rooms_collection = os.getenv('MONGO_ROOMS_COLLECTION')
        mongo_bookings_collection = os.getenv('MONGO_BOOKINGS_COLLECTION')

        self._mongo_clients_collection = mongo_client \
            .get_database(mongo_db) \
            .get_collection(mongo_clients_collection)
        self._mongo_rooms_collection = mongo_client \
            .get_database(mongo_db) \
            .get_collection(mongo_rooms_collection)
        self._mongo_bookings_collection = mongo_client \
            .get_database(mongo_db) \
            .get_collection(mongo_bookings_collection)

    
    async def create_client(self, client: UpdateClient) -> str:
        insert_result = await self._mongo_clients_collection.insert_one(dict(client))
        return str(insert_result.inserted_id)
    

    async def get_client_by_id(self, client_id: str) -> Client:
        client = await self._mongo_users_collection.find_one(filter_by_id(client_id))
        return Client.Map(client)
    

    async def create_room(self, room: UpdateClient) -> str:
        insert_result = await self._mongo_rooms_collection.insert_one(dict(room))
        return str(insert_result.inserted_id)
    

    async def get_room_by_id(self, room_id: str) -> Room:
        room = await self._mongo_users_collection.find_one(filter_by_id(room_id))
        return Room.Map(room)


    async def book_room(self, booking: UpdateBooking) -> str:
        insert_result = await self._mongo_rooms_collection.insert_one(dict(booking))
        return str(insert_result.inserted_id)
    

    async def pay_booking(self, booking_id: str) -> Booking:
        cur_booking = Booking.map(await self._mongo_bookings_collection.find_one(filter_by_booking_id(booking_id)))
        cur_booking.is_paid = True
        booking = await self._mongo_bookings_collection.find_one_and_replace(filter_by_booking_id(booking_id), cur_booking)
        return Booking.map(booking)


    @staticmethod
    def get_instance():
        return MongoRepository()
