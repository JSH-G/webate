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
from app.schemas import event
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
                            content={"status":False, "message":"Sorry, you are not eligible to do this. If you want to create, then contact the admin"})

    return responseDic

@router.put('/update_event', status_code=status.HTTP_200_OK)
def update_event(event_id : str, update: event.EventOut ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):
    
    updte = db.query(models.Create_Event).filter(models.Create_Event.id == event_id)
    check = updte.first()

    if not check:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This event does not exist"})
    
    user_check = db.query(models.Create_Event).filter(models.Create_Event.hotel_id == current_user.id,
                                                      models.Create_Event.id == event_id).first()
    
    if not user_check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"You are not able to perform this action."})
    
    updte.update(update.dict(), synchronize_session=False)
    db.commit()
    return {"status":True ,"message":"Event has been successfully updated"}


@router.delete('/delete_event', status_code=status.HTTP_200_OK)
def delete_event(event_id: str,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):

    dell = db.query(models.Create_Event).filter(models.Create_Event.id == event_id)
    check = dell.first()

    if not check:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This event does not exist"})
        
    user_check = db.query(models.Create_Event).filter(models.Create_Event.hotel_id == current_user.id,
                                                      models.Create_Event.id == event_id).first()
    
    if not user_check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"You are not able to perform this action"})
    
    dell.delete(synchronize_session=False)
    db.commit()

    return {"status":True ,"message":"Event has been successfully deleted."}



@router.get('/get_hotel_event', status_code=status.HTTP_200_OK)
def get_hotel_event(db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_hotel)):

    check = db.query(models.Create_Event).filter(models.Create_Event.hotel_id == current_user.id).all()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "This ID does not exist"})
    
    resp = []
    for test in check:
        usermodel = db.query(models.Create_Event).filter(models.Create_Event.id == test.id).first()
        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Sorry, you have no event"})
        offer_data = {
            'id': usermodel.id,
            'event_name': usermodel.event_name,
            'event_time': usermodel.event_time,
            'event_end_time': usermodel.event_end_time,
            'event_image_vedio': usermodel.event_image_vedio,
            'event_date': usermodel.event_date,
            'longitude':usermodel.longitude,
            'latitude':usermodel.latitude,
            'event_discription': usermodel.discription,
            'is_active': usermodel.is_active
   
        }
    
        resp.append(offer_data)

    return {"status": True, "message": "Success" ,"body": resp}