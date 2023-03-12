from datetime import  datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint


class CreateAdmin(BaseModel):
    name: str
    email: EmailStr
    password: str
    login_type: str
    device_token: str
    is_online: bool
    is_active: bool
    def pre_process(self):
        self.email = self.email.lower()
        