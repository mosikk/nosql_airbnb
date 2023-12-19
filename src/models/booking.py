from datetime import datetime
from pydantic import BaseModel
from typing import Any, Optional


class Booking(BaseModel):
    id: str
    client_id: str
    room_id: str
    is_paid: bool
    # begin_dt: datetime
    # end_dt: datetime

    @classmethod
    def Map(cls, booking: Any):
        if booking is None:
            return None
        return cls(
            id=str(booking['_id']),
            client_id=str(booking['client_id']),
            room_id=str(booking['room_id']),
            is_paid=booking['is_paid'],
        )


class UpdateBooking(BaseModel):
    client_id: str
    room_id: str
    is_paid: bool
    # begin_dt: datetime
    # end_dt: datetime
