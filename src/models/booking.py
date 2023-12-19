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
    def Map(cls, booking: Any):
        if booking is None:
            return None
        return cls(
            id_booking=str(booking['id_booking']),
            id_client=str(booking['id_client']),
            id_room=str(booking['id_room']),
            is_paid=bool(booking['is_paid']),
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
