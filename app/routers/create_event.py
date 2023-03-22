from typing import List, Optional
import uuid, os
from datetime import time, date
from fastapi import HTTPException, Response, UploadFile, status, Depends, APIRouter, Form, File
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app import oauth2
import onesignal_sdk
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime, string, random
from datetime import datetime
from app import oauth2, config
from app.models import models
from app.schemas import offer
from app import utils
import requests
from twilio.rest import Client

router= APIRouter(
    tags=['Create Event']
)

S3_BUCKET_NAME = "codedeskstudio"

client_s3 = boto3.resource(
    service_name = config.settings.service_name,
    region_name = config.settings.region_name,
    aws_access_key_id = config.settings.aws_access_key_id,
    aws_secret_access_key = config.settings.aws_secret_access_key
)

@router.post('/create_event', status_code=status.HTTP_200_OK)
def create_event(event_name: str = Form(...),start_time: time = Form(...),end_time: time = Form(...), event_date: date = Form(...),
                 longitude: str = Form(...),latitude: str = Form(...),discription: str = Form(...),
                  is_active: bool = Form(...),  db: Session = Depends(get_db),event_vedio_image: UploadFile = File(...),
                  current_user: int = Depends(oauth2.get_current_hotel)):
    
    attentication = db.query(models.Create_Event).filter(models.Create_Event.hotel_id == current_user.id).count()

    if attentication < 1 or current_user.is_pro == True:
    
        new_event: models.Create_Event = models.Create_Event()
        new_event.event_name = event_name
        new_event.event_time = start_time
        new_event.event_end_time = end_time
        new_event.event_date = event_date
        new_event.longitude = longitude
        new_event.latitude = latitude
        new_event.discription = discription
        new_event.hotel_id = current_user.id
        new_event.is_active = is_active

        bucket = client_s3.Bucket(S3_BUCKET_NAME)
        noow = str(datetime.now())
        bucket.upload_fileobj(event_vedio_image.file, f"{noow}{event_vedio_image.filename}")
        upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{noow}{event_vedio_image.filename}"
        new_event.event_image_vedio = upload_url


        db.add(new_event)
        db.commit()
        db.refresh(new_event)

        responseDic = {'status': True, 'message' : 'offer created', 
                            'id': new_event.id,
                            'name_offer': new_event.event_name,
                            'event_date': new_event.event_date,
                            'event_date': new_event.event_date,
                            'longitude': new_event.longitude,
                            'latitude': new_event.latitude,
                            'discription': new_event.discription,
                            'event_image_vedio': new_event.event_image_vedio,
                            'hotel_name': current_user.name,
                            'hotel_image': current_user.hotel_image_url
                        }

    else:

        return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            content={"status":False, "message":"Sorry you are not eligble to do this if you want to create then contact to admin"})

        # raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail="Sorry you are not eligble to do this if you want to create then contact to admin")
    return responseDic