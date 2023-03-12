from datetime import  datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint

    
class MenuUpdate(BaseModel):
    menu_name: str
    price: str
    discription: str
    category_id: str
    is_active: bool

class MenuDetail(BaseModel):
    category_name: str
    category_image: str
    class Config:
        orm_mode = True


class MenuOut(BaseModel):
    
    menu_name: str
    menu_image: str
    price: str
    discription: str
    category: MenuDetail
    class Config:
        orm_mode = True

class MenuOutSingel(BaseModel):
    
    menu_name: str
    menu_image: str
    price: str
    discription: str
    class Config:
        orm_mode = True