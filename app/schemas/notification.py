from pydantic import BaseModel



class Notification(BaseModel):
    notify_message: str
    notify_purpose_id: str
    notify_type: str
    notify_send_id: str
    notify_receive_id: str