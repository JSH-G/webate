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

    check = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.email == new_user.email.lower()).first()
    
    if check:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"status":False, "message": "This email is already exist"})
    

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

    new_data = {
        'token_type': 'bearer',
        'access_token':  oauth2.create_access_token(data={"user_id": add_user.id}),
        'id': add_user.id,
        'name': add_user.name,
        'email': add_user.email,
        'device_token': add_user.device_token,
        'otp': otp_update
    }

    return {"status": True, "message": "Successfully SignUp" ,"body": new_data}

@router.post('/email_verification', status_code=status.HTTP_200_OK)
def email_verification(otp: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    if current_user.otp == otp:
        current_user.is_verify = True
        db.commit()
    else:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":f"This otp: {otp} is not correct"})
    

    return {"status": True , "message":"Successfully Verify"}


@router.put('/forget_password_user', status_code=status.HTTP_200_OK)
async def forget_password_user(pss: user.SendEmail, db: Session = Depends(get_db)):

    check = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.email == pss.email)

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

@router.put('/update_user_password', status_code=status.HTTP_200_OK)
def update_user_password(email: str, pss: user.UpdatePassword, db: Session = Depends(get_db)):

    check = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.email == email)

    check_pass = check.first()

    if check_pass:
        hash_password = utils.hash(pss.password)
        pss.password = hash_password
        check.update(pss.dict(), synchronize_session=False)
        db.commit()

    else:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This email is not found"})
    

    return {'status': True, 'message': "Your password updated successfuly"}


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
                            content={"status":False, "message":"you are not able to perform this action"})
    

    return {'status': True, 'message': "Your password change successfuly"}