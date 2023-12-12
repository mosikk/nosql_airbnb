from datetime import datetime
from pydantic import BaseModel


class Booking(BaseModel):
    id_booking: str
    id_client: str
    id_room: str
    status: str
    begin_dt: datetime
    end_dt: datetime
