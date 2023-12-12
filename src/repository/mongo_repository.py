from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorCollection

from utils.mongo_utils import get_db_collection, get_filter
from models.booking import Booking
from models.client import Client
from models.room import Room


class MongoRepository:
    _db_collection: AsyncIOMotorCollection

    def __init__(self, db_collection: AsyncIOMotorCollection):
        self._db_collection = db_collection

    # TODO: add repo functions

    @staticmethod
    def get_instance(db_collection: AsyncIOMotorCollection = Depends(get_db_collection)):
        return MongoRepository(db_collection)
