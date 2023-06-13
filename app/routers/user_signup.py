from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app import oauth2
from app.database import  get_db
from sqlalchemy.orm import Session
import random
from app import oauth2, config
from app.models import models
from app.schemas import user
from app import utils


router= APIRouter(
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

    check = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.email == new_user.email.lower()).first()
    
    if check:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"status":False, "message": "This email already exists."})
    

    add_user = models.User_Sign_Up(otp = otp_update, **new_user.dict())
    db.add(add_user)
    db.commit()
    db.refresh(add_user)

    html = f"""<!DOCTYPE html>
<html>
<head>
  <title>Welcome to We-Bate - Unleash Your Creativity!</title>
</head>
<body>
  <h1>Welcome to We-Bate - Unleash Your Creativity!</h1>
  <p>Dear {add_user.name},</p>
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
        recipients= [new_user.email],
        body=html,
        subtype=MessageType.html)
    fm = FastMail(conf)
    await fm.send_message(message)

    new_data = {
        'token_type': 'bearer',
        'access_token':  oauth2.create_access_token(data={"user_id": add_user.id}),
        'id': add_user.id,
        'name': add_user.name,
        'email': add_user.email,
        'email_verify': add_user.is_verify, 
        'device_token': add_user.device_token,
        'otp': otp_update
    }

    return {"status": True, "message": "Successfully signed up" ,"body": new_data}

@router.post('/send_email_user', status_code=status.HTTP_200_OK)
async def send_email_user(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

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



@router.post('/email_verification', status_code=status.HTTP_200_OK)
def email_verification(otp: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.otp == otp:
        current_user.is_verify = True
        db.commit()
    else:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":f"This otp: {otp} is not correct"})
    

    return {"status": True , "message":"Successfully Verify"}



@router.put('/change_password', status_code=status.HTTP_200_OK)
def change_password(pss: user.UpdatePassword, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    check = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.id == current_user.id)

    check_pass = check.first()

    if check_pass:
        hash_password = utils.hash(pss.password)
        pss.password = hash_password
        check.update(pss.dict(), synchronize_session=False)
        db.commit()

    else:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"You are unable to perform this action."})
    

    return {'status': True, 'message': "Your password has been changed successfully."}


@router.post('/forget_password_user', status_code=status.HTTP_200_OK)
async def forget_password( email: user.Email_Verification, db: Session = Depends(get_db)):

    check_email = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.email == email.email)

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


@router.post('/forget_password_otp_user', status_code=status.HTTP_200_OK)
async def forget_password_otp( otp: user.Otp_Verification, db: Session = Depends(get_db)):

    check_email = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.email == otp.email,
                                                 models.User_Sign_Up.otp == otp.otp).first()

    if not check_email:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Sorry! This OTP not matched"})
    
    return {'status': True, 'message': 'Congratulation,Your Otp is successfully match.'}


@router.put("/forget_update_password_user",status_code=status.HTTP_200_OK)
def update_password( pss: user.Update_Password, db: Session = Depends(get_db)):

    update_password = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.email == pss.email)
    up_pass = update_password.first()

    if not up_pass:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Please! Check your email, this email not exist"})
    

    hash_password = utils.hash(pss.password)
    pss.password = hash_password

    update_password.update(pss.dict(), synchronize_session=False)
    db.commit()

    return { "status": True ,"message": "Congratulations! Your password has been successfully changed."}