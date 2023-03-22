from typing import List, Optional
import uuid, os
from datetime import timedelta
from fastapi import HTTPException, Response, UploadFile, status, Depends, APIRouter, Form, File
from fastapi.responses import JSONResponse
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
    tags=['Offer Scan']
)

@router.get('/get_scan_offer', status_code=status.HTTP_200_OK)
def get_scan_offer_by_hotel(db: Session = Depends(get_db),
               current_user: int = Depends(oauth2.get_current_hotel)):
    
    scan_offer = db.query(models.Offer_Scan).filter(models.Offer_Scan.hotel_id == current_user.id).all()
    
    if not scan_offer:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message":"sorry you have no scane offer"})
    
    res = []
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
            'scan_time': data.scan_time
        }
        res.append(scan_data)

    return {"status": True, "message": "Success", "body": res}


@router.post('/offer_scan', status_code=status.HTTP_200_OK)
def offer_scan(user_id: str, offer_id: str, db: Session = Depends(get_db),
               current_user: int = Depends(oauth2.get_current_hotel)):


    check_offer_id = db.query(models.Create_Offer).filter(models.Create_Offer.id == offer_id,
                                                          models.Create_Offer.hotel_id == current_user.id).first()
    if not check_offer_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False,"message":"this offer is not from your hotel "})
    
    offer_scan = db.query(models.Offer_Scan).filter_by(user_id=user_id, offer_id=offer_id).order_by(models.Offer_Scan.scan_time.desc()).first()

    if offer_scan and (datetime.utcnow() - offer_scan.scan_time) < timedelta(hours=24):

        return JSONResponse(status_code=status.HTTP_409_CONFLICT,
                            content={"status": False, "message": "You already take this offer please wait for complete the time"})

    
    else:

        add_offer = models.Offer_Scan(user_id = user_id, offer_id = offer_id, hotel_id = current_user.id)
        db.add(add_offer)
        db.commit()
        db.refresh(add_offer)

    return {"status":True , "message":"Succesfully scan offer"}
