import pytz
from fastapi import UploadFile, status, Depends, APIRouter, Form, File
from fastapi.responses import JSONResponse
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime
from datetime import datetime
from app import oauth2, config
from app.models import models
from app.schemas import offer
import os


router= APIRouter(
    tags=['Create Offer']
)

S3_BUCKET_NAME = "codedeskstudio"

client_s3 = boto3.resource(
    service_name = config.settings.service_name,
    region_name = config.settings.region_name,
    aws_access_key_id = config.settings.aws_access_key_id,
    aws_secret_access_key = config.settings.aws_secret_access_key
)

@router.post('/create_offer', status_code=status.HTTP_200_OK)
def create_offer(name: str = Form(...),offer_on: str = Form(...),offer_image: UploadFile = File(...),
                 opening: datetime = Form(...),closing: datetime = Form(...),discription: str = Form(...),
                 discount: str = Form(...),is_unlimited: bool = Form(...), price : str = Form(...),
                 db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):
    
    
    new_offer: models.Create_Offer = models.Create_Offer()
    new_offer.name = name
    new_offer.offer_on = offer_on
    new_offer.opening = opening
    new_offer.closing = closing
    new_offer.discription = discription
    new_offer.discount = discount
    new_offer.price = price
    new_offer.hotel_id = current_user.id
    new_offer.is_unlimited = is_unlimited

    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    now = str(datetime.now())
    check = now.replace(".", "_").replace(" ", "_").replace(":", "_")
    filename, extension = os.path.splitext(offer_image.filename)
    modified_filename = f"{check}{filename.replace(' ', '_').replace('.', '')}{extension}"
    bucket.upload_fileobj(offer_image.file, modified_filename)
    upload_url_logo = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{modified_filename}"
    new_offer.offer_image = upload_url_logo

    db.add(new_offer)
    db.commit()
    db.refresh(new_offer)

    responseDic = {
                        'id': new_offer.id,
                        'name_offer': new_offer.name,
                        'offer_on': new_offer.offer_on,
                        'offer_image': new_offer.offer_image,
                        'price': new_offer.price,
                        'opening': new_offer.opening,
                        'closing': new_offer.closing,
                        'discription': new_offer.discription,
                        'discount': new_offer.discount,
                        'is_unlimited': new_offer.is_unlimited,
                        'hotel_name': current_user.name,
                        'hotel_image': current_user.hotel_image_url
                        }

    return {"status": True,"message":"Offer created successfully.","body":responseDic}

@router.put('/update_offer', status_code=status.HTTP_200_OK)
def update_offer(offer_id : str, update: offer.OfferUpdate ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):
    
    updater = db.query(models.Create_Offer).filter(models.Create_Offer.id == offer_id)
    check = updater.first()

    if not check:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This offer not exist"})
    
    user_check = db.query(models.Create_Offer).filter(models.Create_Offer.hotel_id == current_user.id,
                                                      models.Create_Offer.id == offer_id).first()
    if not user_check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"You are not able to perform this action"})
    
    
    updater.update(update.dict(), synchronize_session=False)
    db.commit()
    return {"status":True ,"message":"Offer has been updated successfully."}

@router.delete('/delete_offer', status_code=status.HTTP_200_OK)
def delete_offer(offer_id: str,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):
    print(current_user)

    
    dell = db.query(models.Create_Offer).filter(models.Create_Offer.id == offer_id)
    check = dell.first()

    if not check:

        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This offer not exist"})
        
    user_check = db.query(models.Create_Offer).filter(models.Create_Offer.hotel_id == current_user.id,
                                                      models.Create_Offer.id == offer_id).first()
    
    if not user_check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"You are not able to perform this action"})
    
    dell.delete(synchronize_session=False)
    db.commit()

    return {"status":True ,"message":"Successfully deleted the offer"}


@router.get('/get_hotel_offer', status_code=status.HTTP_200_OK)
def get_hotel_offer(db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_hotel)):

    check = db.query(models.Create_Offer).filter(models.Create_Offer.hotel_id == current_user.id).all()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "This hotel does not exist"})

    resp = []
    for usermodel in check:

        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": " Sorry! sDoes not currently have any offer available."})
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
            'price': usermodel.price,
            'closing': usermodel.closing,
            'discription': usermodel.discription,
            'offer_image': usermodel.offer_image,
            'discount': usermodel.discount,
            'end_date': remaining_time_str,
            'is_unlimited': usermodel.is_unlimited,
            'created_at': usermodel.created_at,
        }
        resp.append(offer_data)

    return {"status": True, "message": "Success" ,"body": resp}

