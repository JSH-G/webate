from datetime import time, date
from pydantic import BaseModel


class EventOut(BaseModel):
    event_name: str
    event_time: time
    event_end_time: time
    event_image_vedio: str
    event_date: date
    is_active: bool
    
    class Config:
        orm_mode = True