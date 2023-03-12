from fastapi import FastAPI, APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from app import oauth2
from typing import List
from app.database import  get_db
from sqlalchemy.orm import Session
from datetime import datetime
from app.models import models
from app.schemas import raitings


router= APIRouter(
    tags=['Hotel Raiting']
)

@router.get('/get_all_raiting', status_code=status.HTTP_200_OK, response_model=List[raitings.Raiting])
def get_all_user(db: Session = Depends(get_db)):
    check = db.query(models.Rating).all()
    return check

@router.post("/ratings", status_code=status.HTTP_200_OK, response_model= raitings.Raiting)
def create_rating(rating: raitings.RatingBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    db_rating = models.Rating(user_id = current_user.id, **rating.dict())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)
    return db_rating

@router.put('/update_raiting', status_code=status.HTTP_200_OK)
def update_raiting(raiting_id: str, updte: raitings.UpdateRaiting, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    check = db.query(models.Rating).filter(models.Rating.id == raiting_id)

    check_user = check.first()

    if not check_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This ID is not exist")
    
    else:
        check.update(updte.dict(), synchronize_session=False)
        db.commit()

    return {'Status': 'Successfully updated'}

@router.delete('/delete_raiting', status_code=status.HTTP_200_OK)
def delete_raiting(raiting_id: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    check = db.query(models.Rating).filter(models.Rating.id == raiting_id)

    check_user = check.first()

    if not check_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="This ID is not exist")
    
    checks = db.query(models.Rating).filter(models.Rating.user_id == current_user.id)

    if not checks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You cann`t able to performed action")
    
    check.delete(synchronize_session=False)
    db.commit()

    return {'Status': 'Successfully Deleted'}
    