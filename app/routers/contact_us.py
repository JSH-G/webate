from typing import List, Optional
import uuid, os
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
from app.schemas import contact_us
from app import utils
import requests
from twilio.rest import Client

router= APIRouter(
    tags=['Contact Us']
)

@router.post("/contact_us", status_code=status.HTTP_200_OK)
def contact_us(add: contact_us.Contact, db: Session = Depends(get_db)):
    check = add.email.lower()
    add.email = check
    db_rating = models.Contact_Us(**add.dict())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating