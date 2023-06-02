from datetime import timedelta
from fastapi import status, Depends, APIRouter
from fastapi.responses import JSONResponse
from app import oauth2
from app.database import  get_db
from sqlalchemy.orm import Session
import datetime
from datetime import datetime
from app import oauth2
from app.models import models



# from gettext import translation, NullTranslations

# def get_translations(lang: Optional[str]) -> NullTranslations:
#     if lang:
#         lang = lang.split("-")[0] # extract language code
#         try:
#             translations = translation("messages", "locales", [lang], fallback=True)
#             return translations
#         except OSError:
#             pass
#     return NullTranslations()

# def _(translations: NullTranslations, message: str) -> str:
#     if translations:
#         return translations.gettext(message)
#     return message


router= APIRouter(
    tags=['Offer Scan']
)



# @router.get('/get_scan_offer_test', status_code=status.HTTP_200_OK)
# def get_scan_offer_by_hotel_test(db: Session = Depends(get_db),
#                current_user: int = Depends(oauth2.get_current_hotel),
#                lang: Optional[str] = Header(None)):
    
#     scan_offer = db.query(models.Offer_Scan).filter(models.Offer_Scan.hotel_id == current_user.id).all()
    
#     if not scan_offer:
#         translations = get_translations(lang)
#         return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
#                             content={"status": False, "message": _(translations, "sorry you have no scan offer")})
    
#     res = []
#     total_scans = 0
#     scans_today = 0
#     today = datetime.now().date()
    
#     for data in scan_offer: 
#         usermodel = db.query(models.Create_Offer).filter(models.Create_Offer.id == data.offer_id).first()

#         if not usermodel:
#             translations = get_translations(lang)
#             return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
#                             content={"status": False, "message": _(translations, "sorry your offer id is not correct")})
        
#         scan_data = {
#             'id': usermodel.id,
#             'offer_name': usermodel.name,
#             'offer_image': usermodel.offer_image,
#             'offer_on': usermodel.offer_on,
#             'discount': usermodel.discount,
#             'scan_time': data.scan_time
#         }
#         res.append(scan_data)
        
#         total_scans += 1
#         if data.scan_time.date() == today:
#             scans_today += 1

#     translations = get_translations(lang)
#     return {"status": True, "message": _(translations, "Success"), "total_scans": total_scans, "scans_today": scans_today, "body": res}




@router.get('/get_scan_offer', status_code=status.HTTP_200_OK)
def get_scan_offer_by_hotel(db: Session = Depends(get_db),
               current_user: int = Depends(oauth2.get_current_hotel)):
    
    scan_offer = db.query(models.Offer_Scan).filter(models.Offer_Scan.hotel_id == current_user.id).order_by(models.Offer_Scan.created_at.desc()).all()
    
    if not scan_offer:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message":"Sorry, you do not have any scan offers."})
    
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
                            content={"status": False, "message": "You have already taken this offer. Please wait for the completion of the specified time"})

    
    else:

        add_offer = models.Offer_Scan(user_id = user_id, offer_id = offer_id, hotel_id = current_user.id)
        db.add(add_offer)
        db.commit()
        db.refresh(add_offer)

    return {"status":True , "message":"You have successfully scanned the offer."}
