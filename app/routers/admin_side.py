from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse
from app.database import  get_db
from sqlalchemy.orm import Session
from app.models import models


router= APIRouter(
    tags=['Admin Side']
)

@router.get('/get_all_hotel_admin', status_code=status.HTTP_200_OK)
def get_all_hotel_admin(db: Session = Depends(get_db)):
    hotels = db.query(models.Hotel_Sign_up).all()

    if not hotels:
        return  JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                             content={"status":False, "message": "Sorry, hotel not found"})

    response = []
    for hotel in hotels:
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        rating_total = sum(rating.rating for rating in ratings) if ratings else 0
        rating_average = rating_total / len(ratings) if ratings else 0
        data = []
        respons = {
            'id': hotel.id,
            'hotel_name': hotel.name,
            'email': hotel.email,
            'gallery': data,
            'hotel_discription': hotel.discription,
            'hotel_pic': hotel.hotel_image_url,
            'hotel_logo': hotel.logo_image_url,
            'rating_total': rating_total,
            'rating_average': round(rating_average, 2)
        }
        response.append(respons)
        check_image = db.query(models.Hotel_Gallery_Image).filter(models.Hotel_Gallery_Image.hotel_id == hotel.id).all()
        for image in check_image:
            image_data = {
                'image_id': image.id,
                'image': image.image
            }
            data.append(image_data)

    return {'status': "true","message":"success","body":response}


@router.get('/get_hotel_info_admin', status_code=status.HTTP_200_OK)
def get_hotel_info_admin(hotel_id: str, db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == hotel_id).first()


    ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
    rating_total = sum(rating.rating for rating in ratings) if ratings else 0
    rating_average = rating_total / len(ratings) if ratings else 0
    data = []
    respons = {
            'id': hotel.id,
            'hotel_name': hotel.name,
            'email': hotel.email,
            'gallery': data, 
            'hotel_description': hotel.discription,
            'longitude': hotel.longitude,
            'latitude':hotel.latitude,
            'phone_number': hotel.phone_number,
            'hotel_pic': hotel.hotel_image_url,
            'hotel_logo': hotel.logo_image_url,
            'upgrade': hotel.is_pro,
            'rating_total': rating_total,
            'rating_average': round(rating_average, 2)
        }
    check_image = db.query(models.Hotel_Gallery_Image).filter(models.Hotel_Gallery_Image.hotel_id == hotel.id).all()
    for image in check_image:
            image_data = {
                'image_id': image.id,
                'image': image.image
            }
            data.append(image_data)

    return {"status": True,"message":"Success","body":respons}