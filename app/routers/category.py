from typing import List, Optional
from fastapi import HTTPException, Response, UploadFile, status, Depends, APIRouter, Form, File
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app import oauth2
import onesignal_sdk
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime, string, random
from datetime import datetime
from app import oauth2, config
from app.models import models
from app import utils
import requests
from twilio.rest import Client

router= APIRouter(
    tags=['Add Category']
)
S3_BUCKET_NAME = "codedeskstudio"

client_s3 = boto3.resource(
    service_name = config.settings.service_name,
    region_name = config.settings.region_name,
    aws_access_key_id = config.settings.aws_access_key_id,
    aws_secret_access_key = config.settings.aws_secret_access_key
)

@router.post('/add_category', status_code=status.HTTP_200_OK)
def add_category(category_name: str = Form(...), image: UploadFile = File(...), db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    add_new:models.Create_category = models.Create_category()
    add_new.category_name = category_name

    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    noow = str(datetime.now())
    bucket.upload_fileobj(image.file, f"{noow}{image.filename}")
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{noow}{image.filename}"
    add_new.category_image = upload_url
    db.add(add_new)
    db.commit()
    db.refresh(add_new)

    return {"status":True,"message":"success","body":add_new}