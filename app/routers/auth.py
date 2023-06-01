from fastapi import APIRouter, Depends, status, HTTPException, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.models import models
from app.database import get_db
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import utils, oauth2
from json import JSONEncoder
from uuid import UUID
JSONEncoder_olddefault = JSONEncoder.default
def JSONEncoder_newdefault(self, o):
    if isinstance(o, UUID): return str(o)
    return JSONEncoder_olddefault(self, o)
JSONEncoder.default = JSONEncoder_newdefault

router = APIRouter(tags=['Authentication'])


@router.post('/login',status_code=status.HTTP_200_OK)
def login(device_token: str = Body(None), user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    user = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.email == user_credentials.username.lower())
    up_pass = user.first()

    if up_pass == None:

        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                            content={"status":False, "message": "Credentials not found"})
    
    if not utils.verify(user_credentials.password, up_pass.password):

        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
                            content={"status":False, "message": "Sorry, password was not found"})
    
    # if not up_pass.is_verify == True:
    #     return JSONResponse(status_code=status.HTTP_403_FORBIDDEN,
    #                         content={"status":False, "message": "please verify your email"})

    

    acees_token = oauth2.create_access_token(data={"user_id": up_pass.id})
    
    Data = {'status': True, 'message' : 'Account Login', 
                            'id': up_pass.id,
                            'name': up_pass.name,
                            'email': up_pass.email,                         
                            'device_token': up_pass.device_token

    }
    user.update({'device_token': str(device_token)}, synchronize_session=False)
    db.commit()

    return {"access_token": acees_token, "token_type":"bearer", "Data_User": Data}