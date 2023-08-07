from pydantic import BaseModel
import uuid
from typing import Optional

class RatingBase(BaseModel):
    rating: float
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
    status: bool = True
    message : str = "Successffully add review"
    Raiting_Review: HotelDetail
    Owner_Name: UserDetail
    rating: float
    comment: Optional[str] = None
    class Config:
        orm_mode = True

class UpdateRaiting(BaseModel):
    rating: float
    comment: Optional[str] = None

class UpdateCategoryName(BaseModel):
    id: str
    category_name: str

class DeleteCategory(BaseModel):
    id: str