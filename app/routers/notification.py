from datetime import timedelta
from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse
from app import oauth2
from app.database import  get_db
from sqlalchemy.orm import Session
import datetime
from datetime import datetime
from app import oauth2
from app.models import models
from app.schemas import notification

router= APIRouter(
    tags=['Notification']
)

@router.post('/add_notification', status_code=status.HTTP_200_OK)
def add_notification(add: notification.Notification, db: Session = Depends(get_db)):

    add_noti = models.Notification(**add.dict())
    db.add(add_noti)
    db.commit()
    db.refresh(add_noti)

    return {'status': True, 'message': 'Success'}

# @router.get()