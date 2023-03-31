from typing import List, Optional
from io import BytesIO
from PIL import Image
import pytz
import qrcode
from fastapi import Response, status, Depends, APIRouter
from fastapi.responses import JSONResponse
from app import oauth2
import onesignal_sdk
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime, string, random
from datetime import datetime, date
from app import oauth2, config
from app.schemas import offer, menu, event
from app.models import models
from twilio.rest import Client

router= APIRouter(
    tags=['Admin Side Hotel']
)

@router.get('/get_all_hotel_admin', status_code=status.HTTP_200_OK)
def get_all_hotel_admin(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):
    hotels = db.query(models.Hotel_Sign_up).all()

    response = []
    for hotel in hotels:
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        rating_total = sum(rating.rating for rating in ratings) if ratings else 0
        rating_average = rating_total / len(ratings) if ratings else 0
        respons = {
            'id': hotel.id,
            'hotel_name': hotel.name,
            'hotel_discription': hotel.discription,
            'longitude': hotel.longitude,
            'latitude':hotel.latitude,
            'phone_number': hotel.phone_number,
            'hotel_pic': hotel.hotel_image_url,
            'hotel_logo': hotel.logo_image_url,
            'rating_total': rating_total,
            'rating_average': round(rating_average, 2)
        }
        response.append(respons)

    return {"status": True,"message":"Success","body":response}


@router.get('/get_scan_offer_admin', status_code=status.HTTP_200_OK)
def get_scan_offer_by_hotel_admin(hotel_id: str ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):
    
    scan_offer = db.query(models.Offer_Scan).filter(models.Offer_Scan.hotel_id == hotel_id).all()
    
    if not scan_offer:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message":"sorry you have no scane offer"})
    
    res = []
    total_scans = 0
    scans_today = 0
    today = datetime.now().date()
    for data in scan_offer: 
        usermodel = db.query(models.Create_Offer).filter(models.Create_Offer.id == data.offer_id).first()

        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message":"sorry your offer id is not correct"})
        
        scan_data = {
            'id': usermodel.id,
            'offer_name': usermodel.name,
            'offer_image': usermodel.offer_image,
            'offer_on': usermodel.offer_on,
            'discount': usermodel.discount,
            'scan_time': data.scan_time,
            'created_at': usermodel.created_at
        }
        res.append(scan_data)
        total_scans += 1
        if data.scan_time.date() == today:
            scans_today += 1

    return {"status": True, "message": "Success","total_scans": total_scans, "scans_today": scans_today, "body": res}

@router.get('/get_admin_resturant_offer', status_code=status.HTTP_200_OK)
def get_admin_resturant_offer(hotel_id: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    
    check = db.query(models.Create_Offer).filter(models.Create_Offer.hotel_id == hotel_id).all()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "This hotel does not exist"})

    resp = []
    for usermodel in check:
        
        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Sorry, this hotel has no offer"})
        tz = pytz.timezone('Europe/Athens')
        remaining_time = usermodel.closing.astimezone(tz) - datetime.now(tz)
        days, seconds = divmod(remaining_time.seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        remaining_time_str = f"{days} days {hours} hours {minutes} minutes"

        offer_data = {
            'id': usermodel.id,
            'name': usermodel.name,
            'offer_on': usermodel.offer_on,
            'closing': usermodel.closing,
            'discription': usermodel.discription,
            'offer_image': usermodel.offer_image,
            'discount': usermodel.discount,
            'end_date': remaining_time_str,
            # 'last_scan': usermodel2,
            'is_unlimited': usermodel.is_unlimited,
            'created_at': usermodel.created_at,
        }
        resp.append(offer_data)

    return {"status": True, "message": "Success" ,"body": resp}



@router.delete('/delete_offer_by_admin', status_code=status.HTTP_200_OK)
def delete_offer_by_admin(offer_id: str,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    
    dell = db.query(models.Create_Offer).filter(models.Create_Offer.id == offer_id)
    check = dell.first()

    if not check:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This offer not exist"})
    
    dell.delete(synchronize_session=False)
    db.commit()

    return {"status":True ,"message":"Successfully deleted the offer by admin"}


@router.put('/update_offer_by_admin', status_code=status.HTTP_200_OK)
def update_offer_by_admin(offer_id : str, update: offer.OfferUpdate ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):
    
    updte = db.query(models.Create_Offer).filter(models.Create_Offer.id == offer_id)
    check = updte.first()

    if not check:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This offer not exist"})
    
    
    updte.update(update.dict(), synchronize_session=False)
    db.commit()
    return {"status":True ,"message":"Successfully updated offer by admin"}


@router.get('/get_admin_resturant_menu', status_code=status.HTTP_200_OK)
def get_admin_resturant_menu(hotel_id: str, category_id: str , db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    check = db.query(models.CreateMenu).filter(models.CreateMenu.hotel_id == hotel_id,
                                               models.CreateMenu.category_id == category_id).all()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message": "Sorry this menu is not added yet"})
    
    resp = []
    for test in check:
        usermodel = db.query(models.CreateMenu).filter(models.CreateMenu.id == test.id).first()
        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "sorry this hotel have no menu"})
        usermodel1 = db.query(models.Create_category).filter(models.Create_category.id == test.category_id).first()
        offer_data = {
            'id': usermodel.id,
            'menu_name': usermodel.menu_name,
            'menu_image': usermodel.menu_image,
            'price': usermodel.price,
            'discription': usermodel.discription,
            'category_name': usermodel1.category_name,
            'category_image': usermodel1.category_image
        }
    
        resp.append(offer_data)

    return {"status": True, "message": "Success" ,"body": resp}


@router.put('/update_menu_by_admin', status_code=status.HTTP_200_OK)
def update_menu_by_admin(menu_id : str, update: menu.MenuUpdate ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):
    
    updte = db.query(models.CreateMenu).filter(models.CreateMenu.id == menu_id)
    check = updte.first()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This menu not exist"})

    
    check_category_id = db.query(models.Create_category).filter(models.Create_category.id == update.category_id).first()
    if not check_category_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This category is not found"})
    
    
    updte.update(update.dict(), synchronize_session=False)
    db.commit()
    return {"status": True ,"message":"Successfully updated menu by admin"}


@router.delete('/delete_menu_by_admin', status_code=status.HTTP_200_OK)
def delete_menu_by_admin(menu_id: str,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    
    dell = db.query(models.CreateMenu).filter(models.CreateMenu.id == menu_id)
    check = dell.first()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message": "This menu not exist"})
    
    dell.delete(synchronize_session=False)
    db.commit()

    return {"status": True , "message": "Successfully deleted the menu by admin"}


@router.get('/get_admin_resturant_event', status_code=status.HTTP_200_OK)
def get_admin_resturant_event(hotel_id: str, db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    check = db.query(models.Create_Event).filter(models.Create_Event.hotel_id == hotel_id).all()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "This id is not exist"})
    
    resp = []
    for test in check:
        usermodel = db.query(models.Create_Event).filter(models.Create_Event.id == test.id).first()
        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "sorry this hotel have no event"})
        offer_data = {
            'id': usermodel.id,
            'event_name': usermodel.event_name,
            'event_time': usermodel.event_time,
            'event_end_time': usermodel.event_end_time,
            'event_image_vedio': usermodel.event_image_vedio,
            'event_date': usermodel.event_date,
            'longitude':usermodel.longitude,
            'latitude':usermodel.latitude,
            'event_discription': usermodel.discription,
            'is_active': usermodel.is_active
   
        }
    
        resp.append(offer_data)

    return {"status": True, "message": "Success" ,"body": resp}


@router.put('/update_event_by_admin', status_code=status.HTTP_200_OK)
def update_event_by_admin(event_id : str, update: event.EventOut ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):
    
    updte = db.query(models.Create_Event).filter(models.Create_Event.id == event_id)
    check = updte.first()

    if not check:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This event not exist"})
    
    updte.update(update.dict(), synchronize_session=False)
    db.commit()
    return {"status":True ,"message":"Successfully updated event by admin"}



@router.delete('/delete_event_by_admin', status_code=status.HTTP_200_OK)
def delete_event_by_admin(event_id: str,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    dell = db.query(models.Create_Event).filter(models.Create_Event.id == event_id)
    check = dell.first()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This event not exist"})
    
    dell.delete(synchronize_session=False)
    db.commit()

    return {"status":True ,"message":"Successfully deleted the event by admin"}


@router.delete('/delete_hotel_by_admin', status_code=status.HTTP_200_OK)
def delete_hotel_by_admin(hotel_id: str,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    dell = db.query(models.User_Sign_Up).filter(models.User_Sign_Up.id == hotel_id)
    check = dell.first()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This hotel not exist"})
    
    dell.delete(synchronize_session=False)
    db.commit()

    return {"status":True ,"message":"Successfully deleted the hotel by admin"}