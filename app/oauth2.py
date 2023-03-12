# from fastapi import Depends, HTTPException, status
# from jose import JWTError
# from jose import jwt
# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session
# from app import database
# from fastapi.security import OAuth2PasswordBearer

# from app.models import models
# from app.schemas import login_schema
# from .config import settings

# oauth2_schema_user = OAuth2PasswordBearer(tokenUrl='login')
# oauth2_schema_hotel = OAuth2PasswordBearer(tokenUrl="loginhotel")
# oauth2_schema_admin = OAuth2PasswordBearer(tokenUrl="loginadmin")

# SECRET_KEY = settings.secret_key
# ALGORITHM = settings.algorithms
# ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire

# def create_acces_token(data: dict):
#     to_encode = data.copy()
#     expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     jwt_encode = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#     return jwt_encode


# def verify_acess_token(token: str, credentials_exception):

#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         id: str = payload.get("user_id")

#         if id is None:
#             raise credentials_exception
#         token_data = login_schema.TokenData(id=id)
        
#     except JWTError:
#         raise credentials_exception

#     return token_data

# def get_current_user(token: str = Depends(oauth2_schema_user), db: Session = Depends(database.get_db)):
#     credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials", headers={"WWW-Authehtication": "Bearer"})

#     token = verify_acess_token(token, credentials_exception)
#     user = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.id == token.id).first()
#     return user

# def get_current_hotel(token: str = Depends(oauth2_schema_hotel), db: Session = Depends(database.get_db)):
#     credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials", headers={"WWW-Authehtication": "Bearer"})

#     token = verify_acess_token(token, credentials_exception)
#     user = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == token.id).first()
#     return user

# def get_current_admin(token: str = Depends(oauth2_schema_admin), db: Session = Depends(database.get_db)):
#     credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials", headers={"WWW-Authehtication": "Bearer"})

#     token = verify_acess_token(token, credentials_exception)
#     user = db.query(models.Admin_Sign_up).filter(models.Admin_Sign_up.id == token.id).first()
#     return user

from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import database
from fastapi.security import OAuth2PasswordBearer

from app.models import models
from app.schemas import login_schema
from .config import settings

oauth2_schema_user = OAuth2PasswordBearer(tokenUrl='login')
oauth2_schema_hotel = OAuth2PasswordBearer(tokenUrl="login_hotel")
oauth2_schema_admin = OAuth2PasswordBearer(tokenUrl="login_admin")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithms
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    jwt_encode = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return jwt_encode


def verify_access_token(token: str, credentials_exception):

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")

        if id is None:
            raise credentials_exception
        token_data = login_schema.TokenData(id=id)

    except JWTError:
        raise credentials_exception

    return token_data


def get_current_user(token: str = Depends(oauth2_schema_user), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.id == token.id).first()
    return user


def get_current_hotel(token: str = Depends(oauth2_schema_hotel), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    user = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == token.id).first()
    return user


def get_current_admin(token: str = Depends(oauth2_schema_admin), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exception)
    user = db.query(models.Admin_Sign_Up).filter(models.Admin_Sign_Up.id == token.id).first()
    return user
