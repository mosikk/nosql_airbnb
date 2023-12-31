from pydantic import BaseModel
from typing import Any, Optional


class Booking(BaseModel):
    id: str
    client_id: str
    room_id: str
    is_paid: bool
    start_dt: str
    end_dt: str

    @classmethod
    def Map(cls, booking: Any):
        if booking is None:
            return None
        return cls(
            id=str(booking['_id']),
            client_id=str(booking['client_id']),
            room_id=str(booking['room_id']),
            is_paid=booking['is_paid'],
            start_dt=str(booking['start_dt']),
            end_dt=str(booking['end_dt'])          
        )


class UpdateBooking(BaseModel):
    client_id: str
    room_id: str
    is_paid: bool
    start_dt: str
    end_dt: str
