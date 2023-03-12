from typing import List, Optional
import uuid, os
from fastapi import HTTPException, Response, status, Depends, APIRouter
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
    # prefix="/posts",
    tags=['User SignUp']
)

conf = ConnectionConfig(
    MAIL_USERNAME =config.settings.mail_username,
    MAIL_PASSWORD = config.settings.mail_password,
    MAIL_FROM = config.settings.mail_from,
    MAIL_PORT = 465,
    MAIL_SERVER = config.settings.mail_server,
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

@router.post('/user_signup', status_code=status.HTTP_200_OK)
async def user_signup(new_user: user.CreateUser, db: Session = Depends(get_db)):

    hash_password = utils.hash(new_user.password)
    new_user.password = hash_password
    otp_update = str(''.join(random.choice('0123456789') for _ in range(4)))
    new_user.pre_process()

    add_user = models.User_Sign_Up(otp = otp_update, **new_user.dict())
    db.add(add_user)
    db.commit()
    db.refresh(add_user)

    html = f"""<h1>This Otp is from webate verfication </h1></br>
                <p><h1>{otp_update}</h1></p></br>
                <h2>If you donot know please contact us +XXXXXXXXX</h2>"""
    
    message = MessageSchema(
        subject="Verification Code",
        recipients= [new_user.email],
        body=html,
        subtype=MessageType.html)
    fm = FastMail(conf)
    await fm.send_message(message)

    return new_user

@router.post('/email_verification', status_code=status.HTTP_200_OK)
def email_verification(otp: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.otp == otp:
        current_user.is_verify = True
        db.commit()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"This otp: {otp} is not correct")
    
    return {"Status": "Successfully Verify"}

