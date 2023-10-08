from fastapi import status,  Depends, APIRouter
from fastapi.responses import JSONResponse
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
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":f"This restaurant didn't exist."})
    like_query = db.query(models.Favorite_Hotel).filter(models.Favorite_Hotel.hotel_id == like.hotel_id,
                                                 models.Favorite_Hotel.user_id == current_user.id)
    found_like = like_query.first()
    if found_like:
        like_query.delete(synchronize_session=False)
        db.commit()
        return JSONResponse(status_code=status.HTTP_200_OK,
            content= { "status": True, "like": False, "message": "Hotel has been successfully remove to favorite."})
        
    new_like = models.Favorite_Hotel(hotel_id = like.hotel_id, user_id = current_user.id)
    db.add(new_like)
    db.commit()
    return {"status": True, "like": True, "message": "Hotel has been successfully added to favorite."}
    


