from datetime import  datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint


class CreateUser(BaseModel):
    name: str
    email: EmailStr
    password: str
    device_token: str
    discription: str
    postal_code: str
    def pre_process(self):
        self.email = self.email.lower()
