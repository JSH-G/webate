from pydantic import BaseModel
import uuid
from typing import Optional

class RatingBase(BaseModel):
    rating: int
    hotel_id: Optional[uuid.UUID]
    comment: Optional[str] = None

class HotelDetail(BaseModel):
    name: str
    class Config:
        orm_mode = True

class UserDetail(BaseModel):
    name: str
    class Config:
        orm_mode = True

class Raiting(BaseModel):
    Raiting_Review: HotelDetail
    Owner_Name: UserDetail
    rating: int
    comment: Optional[str] = None
    class Config:
        orm_mode = True

class UpdateRaiting(BaseModel):
    rating: int
    comment: Optional[str] = None