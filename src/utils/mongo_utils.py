import os
from typing import Any

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection


def filter_by_id(id: str) -> dict:
    return {'_id': ObjectId(id)}


def filter_by_booking_id(id: str) -> dict:
    return {'booking_id': ObjectId(id)}
