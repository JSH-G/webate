from typing import List, Optional
import uuid, os
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
from app.schemas import user
from app import utils
import requests
from twilio.rest import Client

router= APIRouter(
    tags=['Hotel Gallery']
)

S3_BUCKET_NAME = "codedeskstudio"

client_s3 = boto3.resource(
    service_name = config.settings.service_name,
    region_name = config.settings.region_name,
    aws_access_key_id = config.settings.aws_access_key_id,
    aws_secret_access_key = config.settings.aws_secret_access_key
)


@router.post('/image_upload', status_code=status.HTTP_200_OK)
def upload_images(
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_hotel)
):
    is_pro = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == current_user.id).first().is_pro

    max_allowed_images = 10 if is_pro else 3

    existing_images_count = db.query(models.Hotel_Gallery_Image).filter_by(hotel_id=current_user.id).count()
    remaining_images = max_allowed_images - existing_images_count

    if len(images) > remaining_images:
        if is_pro:
            return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                content={'status': False, 'message': 'that Pro Hotel has the ability to upload a maximum of 10 images.'})
        else:
            return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                content= {'status': False, 'message': f'Free hotels can upload a maximum of{remaining_images} more image(s).'})

    resp = []
    for image in images:
        bucket = client_s3.Bucket(S3_BUCKET_NAME)
        noow = str(datetime.now())
        filename = image.filename.replace(" ", "_").replace(".", "_")
        check = noow.replace(".", "_").replace(" ", "_").replace(":", "_")
        bucket.upload_fileobj(image.file, f"{check}{filename}.jpg")
        upload_image = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{check}{filename}.jpg"
        add_image = models.Hotel_Gallery_Image(image=upload_image, hotel_id=current_user.id)
        db.add(add_image)
        db.commit()
        db.refresh(add_image)
        resp.append(upload_image)

    return {'status': True, 'message': 'Success', 'body': resp}


@router.delete('/delete_image', status_code=status.HTTP_200_OK)
def delete_image(image_id: str,db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_hotel)):

    check_image = db.query(models.Hotel_Gallery_Image).filter(models.Hotel_Gallery_Image.id == image_id)

    index = check_image.first()
    if not index:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "This image does not exist"})
    
    if index.hotel_id != current_user.id:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"status": False, "message": "Unable to performed this action"})
    
    check_image.delete(synchronize_session=False)
    db.commit()

    return{"status": True, "message": "image has been successfully deleted."}

