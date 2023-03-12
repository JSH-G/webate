from typing import List, Optional
import uuid
from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from app import oauth2
from app.database import get_db
from app.models import models
from app.schemas import favorite

router = APIRouter(tags=['Add Favorite'])

@router.post("/favorite_hotel", status_code=status.HTTP_200_OK)
def favorite_hotel(like: favorite.FavoriteHotel, db: Session = Depends(get_db), 
                current_user: int = Depends(oauth2.get_current_user)):

    post = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == like.hotel_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The id {like.hotel_id} does not Exist.")
    
    like_qurey = db.query(models.Favorite_Hotel).filter(models.Favorite_Hotel.hotel_id == like.hotel_id,
                                                 models.Favorite_Hotel.user_id == current_user.id)
    

    found_like = like_qurey.first()

    if (like.dir == True):
        if found_like:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
            detail= f"User {current_user.name}, has already like on {like.hotel_id}")
        new_like = models.Favorite_Hotel(hotel_id = like.hotel_id, user_id = current_user.id)
        db.add(new_like)
        db.commit()
        return{"message": "successfully added favorite"}
    else:
        if not found_like:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hotel doesnot exist")

        like_qurey.delete(synchronize_session=False)
        db.commit()

        return {"message": "Successfully deleted favorite"}
    


