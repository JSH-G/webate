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
    tags=['Hotel SignUp']
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

S3_BUCKET_NAME = "codedeskstudio"

client_s3 = boto3.resource(
    service_name = config.settings.service_name,
    region_name = config.settings.region_name,
    aws_access_key_id = config.settings.aws_access_key_id,
    aws_secret_access_key = config.settings.aws_secret_access_key
)

@router.post('/hotel_signup', status_code=status.HTTP_200_OK)
async def hotel_signup(hotel_name: str = Form(...), hotel_discription: str = Form(...), email: str = Form(...), phone_number: str = Form(...),
                       postal_code : str = Form(...), longitude: str = Form(...), latitude: str = Form(...),
                       password: str = Form(...), hotel_image: UploadFile = File(...), hotel_logo: UploadFile = File(...), db: Session = Depends(get_db)):
    hash_password = utils.hash(password)
    new_hotel: models.Hotel_Sign_up = models.Hotel_Sign_up()
    new_hotel.name = hotel_name
    new_hotel.discription = hotel_discription
    new_hotel.email = email.lower()
    new_hotel.phone_number = phone_number
    new_hotel.password = hash_password
    new_hotel.postal_code = postal_code
    new_hotel.longitude  = longitude
    new_hotel.latitude = latitude
    new_hotel.otp = str(''.join(random.choice('0123456789') for _ in range(4)))

    attentication = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.email == email.lower()).first()
    if attentication:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"status": False, "message": "This email is already exist"})

    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    noow = str(datetime.now())
    bucket.upload_fileobj(hotel_image.file, f"{noow}{hotel_image.filename}")
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{noow}{hotel_image.filename}"
    new_hotel.hotel_image_url = upload_url


    bucket.upload_fileobj(hotel_logo.file, f"{noow}{hotel_logo.filename}")
    upload_url_logo = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{noow}{hotel_logo.filename}"
    new_hotel.logo_image_url = upload_url_logo

    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)

    html = f"""<h1>This Otp is from webate verfication </h1></br>
                <p><h1>{new_hotel.otp}</h1></p></br>
                <h2>If you donot know please contact us +XXXXXXXXX</h2>"""
    
    message = MessageSchema(
        subject="Verification Code",
        recipients= [new_hotel.email],
        body=html,
        subtype=MessageType.html)
    fm = FastMail(conf)
    await fm.send_message(message)

    new_data = {
        'token_type': 'bearer',
        'access_token':  oauth2.create_access_token(data={"user_id": new_hotel.id}),
        'id': new_hotel.id,
        'name': new_hotel.name,
        'email': new_hotel.email,
        'otp': new_hotel.otp,
        'discription':new_hotel.discription,
        'phone_number':new_hotel.phone_number,
        'postal_code':new_hotel.postal_code,
        'longitude':new_hotel.longitude,
        'latitude':new_hotel.latitude,
        'hotel_image_url':new_hotel.hotel_image_url,
        'logo_image_url':new_hotel.logo_image_url,
        'device_token': new_hotel.device_token,
    }

    return {"status": True, "message": "Successfully Hotel Added" ,"body": new_data}


@router.post('/email_verification_hotel', status_code=status.HTTP_200_OK)
def email_verification_hotel(otp: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):

    if current_user.otp == otp:
        current_user.is_verify = True
        db.commit()
    else:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":f"This otp: {otp} is not correct"})
    
    return {"status": True , "message":"Successfully Verify"}

@router.put('/forget_password', status_code=status.HTTP_200_OK)
async def forget_password(pss: user.SendEmail, db: Session = Depends(get_db)):

    check = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.email == pss.email)

    check_pass = check.first()

    if check_pass:
        ok = str(''.join(random.choice('0123456789') for _ in range(4)))
        html = f"""<h1>This Otp is from webate verfication </h1></br>
                <p><h1>{ok}</h1></p></br>
                <h2>If you donot know please contact us +XXXXXXXXX</h2>"""
    
        message = MessageSchema(
            subject="Verification Code",
            recipients= [pss.email],
            body=html,
            subtype=MessageType.html)
        fm = FastMail(conf)
        await fm.send_message(message)
        check.update({'otp': ok}, synchronize_session=False)
        db.commit()

    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This email is not found"})
    otp_data  = {
        'otp': ok
    }

    
    return {'status': True, 'message': "Success", 'body': otp_data}

@router.put('/update_hotel_password', status_code=status.HTTP_200_OK)
def update_hotel_password(email: str, pss: user.UpdatePassword, db: Session = Depends(get_db)):

    check = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.email == email)

    check_pass = check.first()

    if check_pass:
        hash_password = utils.hash(pss.password)
        pss.password = hash_password
        check.update(pss.dict(), synchronize_session=False)
        db.commit()

    else:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This email is not found"})
    

    
    return {'status': True ,'message':'Your password updated successfuly'}

@router.put('/change_password_hotel', status_code=status.HTTP_200_OK)
def change_password_hotel(pss: user.UpdatePassword, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):

    check = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == current_user.id)

    check_pass = check.first()

    if check_pass:
        hash_password = utils.hash(pss.password)
        pss.password = hash_password
        check.update(pss.dict(), synchronize_session=False)
        db.commit()

    else:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"you are not able to perform this action"})
    

    return {'status': True, 'message': "Your password change successfuly"}

# @router.post()