from typing import List, Optional
from fastapi import HTTPException, Response, UploadFile, status, Depends, APIRouter, Form, File
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi.responses import JSONResponse
from app import oauth2
import onesignal_sdk
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime, string, random
from datetime import datetime
from app import oauth2, config
from app.models import models
from app.schemas import admin, user
from app import utils
import requests
from twilio.rest import Client

router= APIRouter(
    tags=['Admin SignUp']
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

# @router.post('/admin_signup', status_code=status.HTTP_200_OK)
# async def admin_signup(new_admin: admin.CreateAdmin, db: Session = Depends(get_db)):

#     hash_password = utils.hash(new_admin.password)
#     new_admin.password = hash_password
#     otp_update = str(''.join(random.choice('0123456789') for _ in range(4)))
#     check = new_admin.login_type.lower()
#     new_admin.login_type = check
#     new_admin.pre_process()

#     add_admin = models.Admin_Sign_Up(otp = otp_update, **new_admin.dict())
#     db.add(add_admin)
#     db.commit()
#     db.refresh(add_admin)

#     html = f"""<h1>This Otp is from webate verfication. </h1></br>
#                 <h1>This email is only for Michail Prasianakis athentication. </h1></br>
#                 <p><h1>{otp_update}</h1></p></br>
#                 <h2>If you donot know please contact us +XXXXXXXXX</h2>"""
    
#     message = MessageSchema(
#         subject="Verification Code",
#         recipients= [new_admin.email],
#         body=html,
#         subtype=MessageType.html)
#     fm = FastMail(conf)
#     await fm.send_message(message)

#     new_data = {
#         'token_type': 'bearer',
#         'access_token':  oauth2.create_access_token(data={"user_id": add_admin.id}),
#         'id': add_admin.id,
#         'name': add_admin.name,
#         'email': add_admin.email,
#         'otp': otp_update,
#         'device_token': add_admin.device_token,
#     }

#     return {"status": True, "message": "Successfully SignUp" ,"body": new_data}


@router.post('/email_verification_admin', status_code=status.HTTP_200_OK)
def email_verification_admin(otp: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    if current_user.otp == otp:
        current_user.is_verify = True
        db.commit()
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":f"this otp: {otp} is not correct"})

        # raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"This otp: {otp} is not correct")
    
    return {'status': True, 'message': "Your email successfuly"}

@router.put("/profile_image",status_code=status.HTTP_200_OK)
async def image_url(file: UploadFile, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    safeEmail = current_user.email.replace(".", "_")
    bucket.upload_fileobj(file.file, f"{safeEmail}.jpg")
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{safeEmail}.jpg"

    updateqr = db.query(models.Admin_Sign_Up).filter(models.Admin_Sign_Up.id == current_user.id)
    updateqr.update({'admin_image': upload_url}, synchronize_session=False)
    db.commit()
        
    return {"Message": upload_url}

@router.put('/change_password_admin', status_code=status.HTTP_200_OK)
def change_password_admin(pss: user.UpdatePassword, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    check = db.query(models.Admin_Sign_Up).filter(models.Admin_Sign_Up.id == current_user.id)

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


@router.post('/upgrade_hotel', status_code=status.HTTP_200_OK)
def upgrade_hotel(hotel_id: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    attentication = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == hotel_id).first()

    if attentication:
        attentication.is_pro = True
        db.commit()
    
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
            content={"status": False, "message": f"this user_id {hotel_id} is not exist"})
        
    return {"status": True , "message":"acoount is updated successfully"}