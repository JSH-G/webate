from datetime import  datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr

class Contact(BaseModel):
    name: str
    email: EmailStr
    phone: str
    budget: str
    def pre_process(self):
        self.email = self.email.lower()