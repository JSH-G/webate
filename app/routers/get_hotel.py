from typing import List, Optional
import uuid, os
from fastapi import HTTPException, Response, UploadFile, status, Depends, APIRouter, Form, File
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app import oauth2
import onesignal_sdk
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime, string, random
from datetime import datetime
from app import oauth2, config
from app.models import models
from app.schemas import offer, menu, event, favorite
from app import utils
import requests
from twilio.rest import Client

router= APIRouter(
    tags=['User Side Hotel']
)


@router.get('/get_all_hotel', status_code=status.HTTP_200_OK)
def get_all_hotel(db: Session = Depends(get_db)):
    hotels = db.query(models.Hotel_Sign_up).all()

    response = []
    for hotel in hotels:
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        rating_total = sum(rating.rating for rating in ratings) if ratings else 0
        rating_average = rating_total / len(ratings) if ratings else 0
        respons = {
            'status': "true",
            'id': hotel.id,
            'hotel_name': hotel.name,
            'hotel_discription': hotel.discription,
            'hotel_pic': hotel.hotel_image_url,
            'hotel_logo': hotel.logo_image_url,
            'rating_total': rating_total,
            'rating_average': round(rating_average, 2)
        }
        response.append(respons)

    return response

@router.get('/get_resturant_offer', status_code=status.HTTP_200_OK, response_model=List[offer.OfferOut])
def get_resturant_offer(hotel_id: str, db: Session = Depends(get_db)):

    check = db.query(models.Create_Offer).filter(models.Create_Offer.hotel_id == hotel_id).all()

    return check

@router.get('/get_one_offer', status_code=status.HTTP_200_OK, response_model=offer.OfferOutSingel)
def get_one_offer(offer_id: str, db: Session = Depends(get_db)):

    check = db.query(models.Create_Offer).filter(models.Create_Offer.id == offer_id).first()

    return check


@router.get('/get_resturant_menu', status_code=status.HTTP_200_OK, response_model=List[menu.MenuOut])
def get_resturant_menu(hotel_id: str, category_id: str , db: Session = Depends(get_db)):

    check = db.query(models.CreateMenu).filter(models.CreateMenu.hotel_id == hotel_id,
                                               models.CreateMenu.category_id == category_id).all()
    if not check:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sorry this menu is not added yet")

    return check

@router.get('/get_one_menu', status_code=status.HTTP_200_OK, response_model=menu.MenuOutSingel)
def get_one_menu(menu_id: str, db: Session = Depends(get_db)):

    check = db.query(models.CreateMenu).filter(models.CreateMenu.id == menu_id).first()

    return check

@router.get('/get_resturant_event', status_code=status.HTTP_200_OK, response_model=List[event.EventOut])
def get_resturant_event(hotel_id: str, db: Session = Depends(get_db)):

    check = db.query(models.Create_Event).filter(models.Create_Event.hotel_id == hotel_id).all()

    return check

@router.get('/get_one_event', status_code=status.HTTP_200_OK, response_model=event.EventOut)
def get_one_event(event_id: str, db: Session = Depends(get_db)):

    check = db.query(models.Create_Event).filter(models.Create_Event.id == event_id).first()

    return check


@router.get('/get_all_category', status_code=status.HTTP_200_OK)
def get_category(db: Session = Depends(get_db)):
    check = db.query(models.Create_category).all()
    return check

@router.get('/get_favorite_hotel', status_code=status.HTTP_200_OK)
def get_favorite_hotel(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    get = db.query(models.Favorite_Hotel).filter(models.Favorite_Hotel.user_id == current_user.id).all()

    response = []
    for hotel in get:
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        rating_total = sum(rating.rating for rating in ratings) if ratings else 0
        rating_average = rating_total / len(ratings) if ratings else 0
        check = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == hotel.hotel_id).first()
        respons = {
            'status': "true",
            'id': check.id,
            'hotel_name': check.name,
            'hotel_discription': check.discription,
            'hotel_pic': check.hotel_image_url,
            'hotel_logo': check.logo_image_url,
            'rating_total': rating_total,
            'rating_average': round(rating_average, 2)
        }
        response.append(respons)

    return response

