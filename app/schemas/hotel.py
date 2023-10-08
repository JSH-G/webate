from datetime import  datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint


class CreateHotel(BaseModel):
    id: str
    name: str
    email: EmailStr
    discription: str
    phone_number: str
    longitude: str
    latitude: str
    postal_code: str

class Hotel(BaseModel):
    hotel_id: str