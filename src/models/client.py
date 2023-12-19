from pydantic import BaseModel
from typing import Any


class Client(BaseModel):
    id: str
    name: str

    @classmethod
    def Map(cls, client: Any):
        if client is None:
            return None
        return cls(
            id=str(client['_id']),
            name=str(client['name']),
        )


class UpdateClient(BaseModel):
    name: str
