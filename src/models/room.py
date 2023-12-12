from pydantic import BaseModel


class Room(BaseModel):
    id: str
    address: str
    description: str
    