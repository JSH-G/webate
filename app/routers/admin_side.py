from typing import List, Optional
import uuid, os
from fastapi import HTTPException, Response, UploadFile, status, Depends, APIRouter, Form, File
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi.responses import JSONResponse
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

