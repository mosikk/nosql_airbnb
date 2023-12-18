from datetime import datetime
from pydantic import BaseModel
from typing import Any, Optional


class Booking(BaseModel):
    id_booking: str
    id_client: str
    id_room: str
    is_paid: bool
    begin_dt: Optional[datetime]
    end_dt: Optional[datetime]

    @classmethod
    def Map(cls, client: Any):
        return cls(
            id_booking=str(client['id_booking']),
            id_client=str(client['id_client']),
            id_room=str(client['id_room']),
            is_paid=client['is_paid'],
        )


class UpdateBooking(BaseModel):
    id_client: str
    id_room: str
    is_paid: bool
    begin_dt: Optional[datetime]
    end_dt: Optional[datetime]

    def __post_init__(self):
        if self.is_paid is None:
            self.is_paid = False
