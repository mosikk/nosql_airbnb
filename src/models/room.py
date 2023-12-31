from pydantic import BaseModel
from typing import Any


class Room(BaseModel):
    id: str
    name: str
    country: str
    city: str
    address: str
    description: str

    @classmethod
    def Map(cls, room: Any):
        if room is None:
            return None
        return cls(
            id=str(room['_id']),
            name=str(room['name']),
            country=str(room['country']),
            city=str(room['city']),
            address=str(room['address']),
            description=str(room['description']),
        )


class UpdateRoom(BaseModel):
    name: str
    country: str
    city: str
    address: str
    description: str