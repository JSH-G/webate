from pydantic import BaseModel
from typing import Optional
import uuid

class FavoriteHotel(BaseModel):
    hotel_id: str
    dir:  bool = True

class HotelDetail(BaseModel):
    name: str
    discription: str
    hotel_image_url: str
    logo_image_url: str
    longitude: str
    latitude: str
    class Config:
        orm_mode = True

class ShowFavorite(BaseModel):
    Hotel_Name: HotelDetail
    class Config:
        orm_mode = True