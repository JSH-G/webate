from fastapi import  UploadFile, status, Depends, APIRouter, Form, File
from fastapi.responses import JSONResponse
from app import oauth2
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime
from datetime import datetime
from app import oauth2, config
from app.models import models
from app.schemas import menu
import os

router= APIRouter(
    tags=['Create Menu']
)
S3_BUCKET_NAME = "codedeskstudio"

client_s3 = boto3.resource(
    service_name = config.settings.service_name,
    region_name = config.settings.region_name,
    aws_access_key_id = config.settings.aws_access_key_id,
    aws_secret_access_key = config.settings.aws_secret_access_key
)

@router.post('/create_menu', status_code=status.HTTP_200_OK)
def create_menu(name: str = Form(...),price: str = Form(...),menu_image: UploadFile = File(...),
                discription: str = Form(...),category_id: str = Form(...),
                db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):
    
    check1 = db.query(models.Create_category).filter(models.Create_category.id == category_id).first()

    if not check1:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This ID does not exist"})
    


    new_menu: models.CreateMenu = models.CreateMenu()
    new_menu.menu_name = name
    new_menu.price = price
    new_menu.discription = discription
    new_menu.hotel_id = current_user.id
    new_menu.category_id = category_id

    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    now = str(datetime.now())
    check = now.replace(".", "_").replace(" ", "_").replace(":", "_")
    filename, extension = os.path.splitext(menu_image.filename)
    modified_filename = f"{check}{filename.replace(' ', '_').replace('.', '')}{extension}"
    bucket.upload_fileobj(menu_image.file, modified_filename)
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{modified_filename}"
    new_menu.menu_image = upload_url


    db.add(new_menu)
    db.commit()
    db.refresh(new_menu)

    responseDic = {'status': True, 'message' : 'menu created', 
                        'id': new_menu.id,
                        'menu_name': new_menu.menu_name,
                        'price': new_menu.price,
                        'discription': new_menu.discription,
                        'menu_image': new_menu.menu_image,
                        'category': check1.category_name,
                        'hotel_name': current_user.name,
                        'hotel_image': current_user.hotel_image_url
                        }

    return responseDic

@router.put('/update_menu', status_code=status.HTTP_200_OK)
def update_menu(update: menu.MenuUpdate ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):
    
    check_menu = db.query(models.CreateMenu).filter(models.CreateMenu.id == update.id)
    check = check_menu.first()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This menu does not exist"})

    
    check_category_id = db.query(models.Create_category).filter(models.Create_category.id == update.category_id).first()
    if not check_category_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This category is not found"})
    
    # user_check = db.query(models.CreateMenu).filter(models.CreateMenu.hotel_id == current_user.id,
    #                                                   models.CreateMenu.id == menu_id).first()
    # if not user_check:
    #     return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
    #                         content={"status":False, "message":"You are not able to perform this action"})
    
    
    check_menu.update(update.dict(), synchronize_session=False)
    db.commit()

    return {"status": True ,"message":"Menu has been updated successfully."}


@router.put('/update_menu_image', status_code=status.HTTP_200_OK)
def update_menu_image(menu_id: str = Form(...), menu_image: UploadFile = File(...), db: Session = Depends(get_db), 
                       current_user: int = Depends(oauth2.get_current_hotel)):

    updater = db.query(models.CreateMenu).filter(models.CreateMenu.id == menu_id)
    check = updater.first()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"This offer not exist"})

    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    now = str(datetime.now())
    check = now.replace(".", "_").replace(" ", "_").replace(":", "_")
    filename, extension = os.path.splitext(menu_image.filename)
    modified_filename = f"{check}{filename.replace(' ', '_').replace('.', '')}{extension}"
    bucket.upload_fileobj(menu_image.file, modified_filename)
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{modified_filename}"

    updater.update({"menu_image": upload_url}, synchronize_session=False)
    db.commit()

    return {"status":True ,"message":"Menu has been updated successfully."}



@router.delete('/delete_menu', status_code=status.HTTP_200_OK)
def delete_menu(menu_id: str,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_hotel)):

    
    dell = db.query(models.CreateMenu).filter(models.CreateMenu.id == menu_id)
    check = dell.first()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message": "This menu does not exist"})
    
    user_check = db.query(models.CreateMenu).filter(models.CreateMenu.hotel_id == current_user.id,
                                                      models.CreateMenu.id == menu_id).first()
    
    if not user_check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"You are not able to perform this action"})

    dell.delete(synchronize_session=False)
    db.commit()

    return {"Status": "Menu has been successfully deleted."}




# @router.get('/get_hotel_menu', status_code=status.HTTP_200_OK)
# def get_hotel_menu(category_id: str , db: Session = Depends(get_db),current_user: int = Depends(oauth2.get_current_hotel)):

#     check = db.query(models.CreateMenu).filter(models.CreateMenu.hotel_id == current_user.id,
#                                                models.CreateMenu.category_id == category_id).all()
#     if not check:
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
#                             content={"status":False, "message":"Sorry! Menu has not been added yet"})
    
#     resp = []
#     for test in check:
#         usermodel = db.query(models.CreateMenu).filter(models.CreateMenu.id == test.id).first()
#         if not usermodel:
#             return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
#                             content={"status": False, "message": "Sorry, this hotel has no menu"})
#         usermodel1 = db.query(models.Create_category).filter(models.Create_category.id == test.category_id).first()
#         offer_data = {
#             'id': usermodel.id,
#             'menu_name': usermodel.menu_name,
#             'menu_image': usermodel.menu_image,
#             'price': usermodel.price,
#             'discription': usermodel.discription,
#             'category_name': usermodel1.category_name,
#             'category_image': usermodel1.category_image
#         }
    
#         resp.append(offer_data)

#     return {"status": True, "message": "Success" ,"body": resp}