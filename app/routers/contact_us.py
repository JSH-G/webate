from fastapi import  status, Depends, APIRouter
from app.database import  get_db
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import contact_us
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
    return {"status":True,"message":"success","body":db_rating}