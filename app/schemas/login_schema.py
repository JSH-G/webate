from datetime import  datetime
import uuid
from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic.types import conint



class TokenData(BaseModel):
    id: Optional[str] = None
