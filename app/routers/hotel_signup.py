import os
from fastapi import UploadFile, status, Depends, APIRouter, Form, File
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app import oauth2
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime,  random
from datetime import datetime
from app import oauth2, config
from app.models import models
from app.schemas import user
from app import utils

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

    authentication = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.email == email.lower()).first()
    if authentication:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"status": False, "message": "This email already exists."})


    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    safeEmail = new_hotel.email.replace(".", "_")
    bucket.upload_fileobj(hotel_image.file, f"{safeEmail}.jpg")
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{safeEmail}.jpg"    
    new_hotel.hotel_image_url = upload_url


    now = str(datetime.now())
    check = now.replace(".", "_").replace(" ", "_").replace(":", "_")
    filename, extension = os.path.splitext(hotel_logo.filename)
    modified_filename = f"{check}{filename.replace(' ', '_').replace('.', '')}{extension}"
    bucket.upload_fileobj(hotel_logo.file, modified_filename)
    upload_url_logo = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{modified_filename}"
    new_hotel.logo_image_url = upload_url_logo

    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)

    html = f"""<h1>This Otp is from We-Bate verification </h1></br>
                <p><h1>{new_hotel.otp}</h1></p></br>
                <h2>If you don't know please contact us +XXXXXXXXX</h2>"""
    
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

    return {"status": True, "message": "The hotel was successfully added" ,"body": new_data}



@router.put("/update_hotel_image",status_code=status.HTTP_200_OK)
async def update_hotel_image(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):

    updater = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == current_user.id)
    post = updater.first()

    if post == None:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                content={"status": False, "message":"You are not authorized to perform this action."})

    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    safeEmail = current_user.email.replace(".", "_")
    bucket.upload_fileobj(file.file, f"{safeEmail}.jpg")
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{safeEmail}.jpg"

    updater.update({'hotel_image_url': upload_url}, synchronize_session=False)
    db.commit()
        
    return {"status":True, "message": "Congratulations, your image has been successfully uploaded!", "body": upload_url}

@router.put("/update_hotel_logo",status_code=status.HTTP_200_OK)
async def update_hotel_logo(logo: UploadFile = File(...), db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):

    updater = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == current_user.id)
    post = updater.first()

    if post == None:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                content={"status": False, "message":"You are not authorized to perform this action."})
    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    now = str(datetime.now())
    check = now.replace(".", "_").replace(" ", "_").replace(":", "_")
    filename, extension = os.path.splitext(logo.filename)
    modified_filename = f"{check}{filename.replace(' ', '_').replace('.', '')}{extension}"
    bucket.upload_fileobj(logo.file, modified_filename)
    upload_url_logo = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{modified_filename}"

    updater.update({'logo_image_url': upload_url_logo}, synchronize_session=False)
    db.commit()
        
    return {"status":True, "message": "Congratulations, your image has been successfully uploaded!", "body": upload_url_logo}



@router.post('/email_verification_hotel', status_code=status.HTTP_200_OK)
def email_verification_hotel(otp: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):

    if current_user.otp == otp:
        current_user.is_verify = True
        db.commit()
    else:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":f"This otp: {otp} is not correct"})
    
    return {"status": True , "message":"The verification process was successful."}



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
    

    return {'status': True, 'message': "Your password has changed successfully."}


@router.post('/forget_password_hotel', status_code=status.HTTP_200_OK)
async def forget_password( email: user.Email_Verification, db: Session = Depends(get_db)):

    check_email = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.email == email.email)

    if not check_email.first():
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Please! Check your email, this email not exist"})
    

    otp1 = str(''.join(random.choice('0123456789') for _ in range(4)))

    html = f"""<p>{otp1}</p> """
    message = MessageSchema(
        subject="Forget Password",
        recipients= [email.email],
        body=html,
        subtype=MessageType.html)
    fm = FastMail(conf)
    await fm.send_message(message)

    check_email.update({'otp': otp1}, synchronize_session=False)
    db.commit()

    return {'status': True, 'message': 'We have sent a verification code to your email', 'body': otp1}



@router.post('/forget_password_otp', status_code=status.HTTP_200_OK)
async def forget_password_otp( otp: user.Otp_Verification, db: Session = Depends(get_db)):

    check_email = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.email == otp.email,
                                                 models.Hotel_Sign_up.otp == otp.otp).first()

    if not check_email:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Sorry! This OTP not matched"})
    
    return {'status': True, 'message': 'Congratulation,Your Otp is successfully match.'}


@router.put("/forget_update_password",status_code=status.HTTP_200_OK)
def update_password( pss: user.Update_Password, db: Session = Depends(get_db)):

    update_password = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.email == pss.email)
    up_pass = update_password.first()

    if not up_pass:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Please! Check your email, this email not exist"})
    

    hash_password = utils.hash(pss.password)
    pss.password = hash_password

    update_password.update(pss.dict(), synchronize_session=False)
    db.commit()

    return { "status": True ,"message": "Congratulations! Your password has been successfully changed."}

@router.post('/send_email_hotel', status_code=status.HTTP_200_OK)
async def send_email_hotel(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):

    # if current_user.is_verify == True:
    #     return JSONResponse(status_code=status.HTTP_409_CONFLICT,
    #                         content={"status":False, "message": "Your email already verify"})
    check = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.id == current_user.id)

    if check.first().is_verify == True:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"status":False, "message": "Your email already verify"})

    otp_update = str(''.join(random.choice('0123456789') for _ in range(4)))
    check.update({'otp': otp_update}, synchronize_session=False)
    db.commit()
    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Welcome to We-Bate - Unleash Your Creativity!</title>
</head>
<body>
  <h1>Welcome to We-Bate - Unleash Your Creativity!</h1>
  <p>Dear {current_user.name},</p>
  <p>Congratulations! You've successfully joined We-Bate, the ultimate platform for unleashing your creativity and connecting with fellow artists. We're thrilled to have you on board, and we can't wait to see the incredible masterpieces you'll create!</p>
  <p>Now that your account is all set up, let's dive into the world of endless inspiration and artistic collaboration. But before we begin, we need to verify your account with a unique One-Time Password (OTP).</p>
  <p>Here's your personalized OTP: <strong>{otp_update}</strong>. Please keep it handy as you'll need it to access all the exciting features awaiting you.</p>
  <p>Follow these steps to get started on your artistic journey:</p>
  <p>With We-Bate, you have a platform to express yourself, receive feedback, and grow as an artist. We're committed to providing a supportive and vibrant community that nurtures your creativity.</p>
  <p>If you have any questions, need guidance, or simply want to share your experience, our friendly support team is here to assist you. We're just an email away!</p>
  <p>Get ready to immerse yourself in a world of artistry, [User]. We're excited to witness the magic you'll create on We-Bate. Let your creativity soar!</p>
  <p>Best regards,</p>
  <p>The We-Bate Team</p>
</body>
</html>"""
    message = MessageSchema(
        subject="Verification Code",
        recipients= [current_user.email],
        body=html,
        subtype=MessageType.html)
    fm = FastMail(conf)
    await fm.send_message(message)

    return {'status': True, 'message': 'Successfully otp send', "otp": otp_update}