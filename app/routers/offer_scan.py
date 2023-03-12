from typing import List, Optional
import uuid, os
from datetime import timedelta
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
    tags=['Offer Scan']
)

@router.post('/offer_scan', status_code=status.HTTP_200_OK)
def offer_scan(qr_number: str, user_id: str, offer_id: str, db: Session = Depends(get_db),
               current_user: int = Depends(oauth2.get_current_hotel)):

    check_qr = db.query(models.Create_Offer).filter(models.Create_Offer.qr_number == qr_number).first()
    if not check_qr:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Check Qr code please", status= True)
    
    offer_scan = db.query(models.Offer_Scan).filter_by(user_id=user_id, offer_id=offer_id).order_by(models.Offer_Scan.scan_time.desc()).first()

    if offer_scan and (datetime.utcnow() - offer_scan.scan_time) < timedelta(hours=24):

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="You need to wait until the offer time complete")
    
    else:

        add_offer = models.Offer_Scan(user_id = user_id, offer_id = offer_id, hotel_id = current_user.id)
        db.add(add_offer)
        db.commit()
        db.refresh(add_offer)

    return {"Status":"Succesfully scan offer"}
