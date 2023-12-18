from pydantic import BaseModel
from typing import Any, Optional


class Room(BaseModel):
    id: str
    address: str
    description: Optional[str]

    @classmethod
    def Map(cls, room: Any):
        return cls(
            id=str(room['_id']),
            address=room['address'],
            description=room['description'],
        )


class UpdateRoom(BaseModel):
    address: str
    description: Optional[str]
