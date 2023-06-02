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
    def pre_process(self):
        self.email = self.email.lower()

class SendEmail(BaseModel):
    email: EmailStr

class UpdatePassword(BaseModel):
    password: str


class Email_Verification(BaseModel):
    email: EmailStr


class Otp_Verification(BaseModel):
    email: EmailStr
    otp: str

class Update_Password(BaseModel):
    email: EmailStr
    password: str