from pydantic import BaseModel
from typing import Any


class Room(BaseModel):
    id: str
    name: str
    address: str
    description: str

    @classmethod
    def Map(cls, room: Any):
        if room is None:
            return None
        return cls(
            id=str(room['_id']),
            name=str(room['name']),
            address=str(room['address']),
            description=str(room['description']),
        )


class UpdateRoom(BaseModel):
    name: str
    address: str
    description: str
