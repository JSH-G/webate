from datetime import  datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint


class OfferUpdate(BaseModel):
    name: str
    offer_on: str
    opening: str
    closing: str
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