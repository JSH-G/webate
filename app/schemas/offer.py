from datetime import  datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint


class OfferUpdate(BaseModel):
    id: str
    name: str
    offer_on: str
    opening: datetime
    closing: datetime
    price: str
    discription: str
    discount: str
    is_unlimited: bool 

class OfferOut(BaseModel):
    name: str
    offer_on: str
    closing: str
    discription: str
    offer_image: str
    discount: str
    is_unlimited: bool
    created_at: datetime
    class Config:
        orm_mode = True

class OfferOutSingel(BaseModel):
    name: str
    offer_on: str
    closing: str
    qr_number: str
    qr_image: str
    discription: str
    offer_image: str
    discount: str
    is_unlimited: bool 
    class Config:
        orm_mode = True

class HotelUser(BaseModel):
    id: Optional[uuid.UUID]
    name: str
    class Config:
        orm_mode = True

class ScanOffer(BaseModel):
    Hotel_Data: HotelUser
    Offer_Data: OfferOut
    class Config:
        orm_mode = True