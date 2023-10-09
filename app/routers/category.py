from fastapi import UploadFile, status, Depends, APIRouter, Form, File
from fastapi.responses import JSONResponse
from app import oauth2
from app.database import  get_db
from sqlalchemy.orm import Session
import boto3, datetime
from datetime import datetime
from app import oauth2, config
from app.models import models
from app.schemas import raitings
import os

router= APIRouter(
    tags=['Add Category']
)
S3_BUCKET_NAME = "codedeskstudio"

client_s3 = boto3.resource(
    service_name = config.settings.service_name,
    region_name = config.settings.region_name,
    aws_access_key_id = config.settings.aws_access_key_id,
    aws_secret_access_key = config.settings.aws_secret_access_key
)

@router.post('/add_category', status_code=status.HTTP_200_OK)
def add_category(category_name: str = Form(...), 
                 image: UploadFile = File(...), 
                 db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    add_new:models.Create_category = models.Create_category()
    add_new.category_name = category_name

    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    now = str(datetime.now())
    check = now.replace(".", "_").replace(" ", "_").replace(":", "_")
    filename, extension = os.path.splitext(image.filename)
    modified_filename = f"{check}{filename.replace(' ', '_').replace('.', '')}{extension}"
    bucket.upload_fileobj(image.file, modified_filename)
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{modified_filename}"
    add_new.category_image = upload_url
    db.add(add_new)
    db.commit()
    db.refresh(add_new)

    return {"status":True,"message":"success","body":add_new}

@router.put('/update_category_image', status_code=status.HTTP_200_OK)
def update_category_image(category_id: str = Form(...), image: UploadFile = File(...), 
                          db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):
    
    check_id = db.query(models.Create_category).filter(models.Create_category.id == category_id)

    if not check_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={'status': False, 'message': 'This id not exist'})
    
    bucket = client_s3.Bucket(S3_BUCKET_NAME)
    now = str(datetime.now())
    check = now.replace(".", "_").replace(" ", "_").replace(":", "_")
    filename, extension = os.path.splitext(image.filename)
    modified_filename = f"{check}{filename.replace(' ', '_').replace('.', '')}{extension}"
    bucket.upload_fileobj(image.file, modified_filename)
    upload_url = f"https://{S3_BUCKET_NAME}.s3.ap-northeast-1.amazonaws.com/{modified_filename}"


    check_id.update({'category_image': upload_url}, synchronize_session=False)
    db.commit()

    return {'status': True, 'message': 'Successfully, Category Image update'}




@router.put('/update_category_name', status_code=status.HTTP_200_OK)
def update_category_name(add: raitings.UpdateCategoryName ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    check_id = db.query(models.Create_category).filter(models.Create_category.id == add.id)

    if not check_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={'status': False, 'message': 'This id not exist'})
    
    check_id.update(add.dict(), synchronize_session=False)
    db.commit()

    return{'status': True, 'message': 'Successfully, Update category the name'}

@router.delete('/delete_category',status_code=status.HTTP_200_OK)
def delete_category(dell: raitings.DeleteCategory ,db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_admin)):

    check_id = db.query(models.Create_category).filter(models.Create_category.id == dell.id)

    if not check_id:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={'status': False, 'message': 'This id not exist'})
    
    check_id.delete(synchronize_session=False)
    db.commit()

    return {'status': True, 'message': 'Successfully, Delete category now no data against this category is deleted(included menu as well)'}
