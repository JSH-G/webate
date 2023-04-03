from fastapi import APIRouter, status, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app import oauth2
from typing import List
from app.database import  get_db
from sqlalchemy.orm import Session
from app.models import models
from app.schemas import raitings


router= APIRouter(
    tags=['Hotel Raiting']
)

@router.get('/get_all_raiting', status_code=status.HTTP_200_OK)
def get_all_user(db: Session = Depends(get_db)):
    check = db.query(models.Rating).order_by(models.Rating.created_at.desc()).all()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "This id is not exist"})
    resp = []
    for test in check:
        usermodel = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == test.hotel_id).first()
        usermodel2 = db.query(models.Rating).filter(models.Rating.id == test.id).first()
        usermodel3= db.query(models.User_Sign_Up).filter(models.User_Sign_Up.id == test.user_id ).first()
        new_data = {
                
            'hotel_name': usermodel.name,
            'owner_name': usermodel3.name,
            'id_': test.id,
            'raiting': usermodel2.rating,
            'comment': usermodel2.comment
        }
        resp.append(new_data)

    return {"status": True, "message": "Success" ,"body": resp}

@router.post("/ratings", status_code=status.HTTP_200_OK)
def create_rating(rating: raitings.RatingBase, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    attentication = db.query(models.Rating).filter(models.Rating.hotel_id == rating.hotel_id,
                                                   models.Rating.user_id == current_user.id).first()
    
    if attentication:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"status":False, "message":"you already rate this hotel"})
    
    db_rating = models.Rating(user_id = current_user.id, **rating.dict())
    db.add(db_rating)
    db.commit()
    db.refresh(db_rating)

    usermodel = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == rating.hotel_id).first()
    new_data = {
            
        'hotel_name': usermodel.name,
        'owner_name': current_user.name,
        'id_': db_rating.id,
        'raiting': db_rating.rating,
        'comment': db_rating.comment
    }

    return {"status": True, "message": "Success" ,"body": new_data}

@router.put('/update_raiting', status_code=status.HTTP_200_OK)
def update_raiting(raiting_id: str, updte: raitings.UpdateRaiting, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    check = db.query(models.Rating).filter(models.Rating.id == raiting_id)

    check_user = check.first()

    if not check_user:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This ID is not exist"})
        
    else:
        check.update(updte.dict(), synchronize_session=False)
        db.commit()

    return {'status': True ,"message":'Successfully updated'}

@router.delete('/delete_raiting', status_code=status.HTTP_200_OK)
def delete_raiting(raiting_id: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    check = db.query(models.Rating).filter(models.Rating.id == raiting_id)

    check_user = check.first()

    if not check_user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This ID is not exist"})
        
    checks = db.query(models.Rating).filter(models.Rating.user_id == current_user.id)

    if not checks:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"You cann't able to performed action"})
    
    
    check.delete(synchronize_session=False)
    db.commit()

    return {'status': True ,"message":'Successfully Deleted'}
    