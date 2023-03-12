from passlib.context import CryptContext
from datetime import date

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash(password: str):
    return pwd_context.hash(password)

def verify(plain_password, hash_password):
    return pwd_context.verify(plain_password, hash_password)

# def age(date_of_birth: date):
#     today = date.today()
#     print(today)
#     age = today - date_of_birth
#     return age