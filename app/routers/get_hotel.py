from io import BytesIO
from typing import List
import pytz
import qrcode
from fastapi import Response, status, Depends, APIRouter, Form
from fastapi.responses import JSONResponse
from app import oauth2
from app.database import  get_db
from sqlalchemy.orm import Session
import  datetime
from datetime import datetime
from app import oauth2
from app.models import models

router= APIRouter(
    tags=['User Side Hotel']
)


# @router.post('/notification', status_code=status.HTTP_200_OK)
# def notification(hotel_ids: List[str] = Form(...), db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

#     check_array = hotel_ids[0].split(',')

#     resp = []
#     for hotel_id in check_array:
#         check_favorite = db.query(models.Favorite_Hotel).filter(models.Favorite_Hotel.hotel_id == hotel_id,
#                                                                 models.Favorite_Hotel.user_id == current_user.id).first()
        
#         if check_favorite:

#             supermodel = True
#         else:
#             supermodel = False
        
#         check_pro = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == hotel_id,
#                                                         models.Hotel_Sign_up.is_pro == True).first()
#         if check_pro:

#             supermodel1 = True
#         else:
#             supermodel1 = False
        
#         data = {
#             'hotel_id': hotel_id,
#             'is_favorite': supermodel,
#             'hotel_upgrade': supermodel1
#         }
#         resp.append(data)

#     return {'status': True, 'message': 'success', 'body': resp}

@router.get('/get_hotel_info', status_code=status.HTTP_200_OK)
def get_hotel_info(hotel_id: str, db: Session = Depends(get_db)):
    hotel = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == hotel_id).first()

    # get_favorite = db.query(models.Favorite_Hotel).filter(models.Favorite_Hotel.hotel_id == hotel.id,
    #                                                           models.Favorite_Hotel.user_id == current_user.id).first()
    # if get_favorite:
    #     usermodel3 = True
    # else:
        # usermodel3 = False


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
            'longitude': hotel.longitude,
            'latitude':hotel.latitude,
            'phone_number': hotel.phone_number,
            'hotel_pic': hotel.hotel_image_url,
            'hotel_logo': hotel.logo_image_url,
            'upgrade': hotel.is_pro,
            # 'favorite' : usermodel3,
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


@router.get('/get_all_hotel', status_code=status.HTTP_200_OK)
def get_all_hotel(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):
    hotels = db.query(models.Hotel_Sign_up).order_by(models.Hotel_Sign_up.created_at.desc()).all()

    response = []
    for hotel in hotels:
        get_rating = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id,
                                                    models.Rating.user_id == current_user.id).first()
        if get_rating:
            usermodel4 = True
        else:
            usermodel4 = False
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        get_favorite = db.query(models.Favorite_Hotel).filter(models.Favorite_Hotel.hotel_id == hotel.id,
                                                              models.Favorite_Hotel.user_id == current_user.id).first()
        if get_favorite:
            usermodel3 = True
        else:
            usermodel3 = False
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        rating_total = sum(rating.rating for rating in ratings) if ratings else 0
        rating_average = rating_total / len(ratings) if ratings else 0
        data = []
        offers = []
        respons = {
            'id': hotel.id,
            'hotel_name': hotel.name,
            'hotel_discription': hotel.discription,
            'email': hotel.email,
            'gallery': data, 
            'longitude': hotel.longitude,
            'latitude':hotel.latitude,
            'phone_number': hotel.phone_number,
            'hotel_pic': hotel.hotel_image_url,
            'hotel_logo': hotel.logo_image_url,
            'upgrade': hotel.is_pro,
            'favorite' : usermodel3,
            'rate_this_hotel': usermodel4,
            'rating_total': rating_total,
            'rating_average': round(rating_average, 1),
            'hotel_offers': offers
        }
        response.append(respons)

        check_image = db.query(models.Hotel_Gallery_Image).filter(models.Hotel_Gallery_Image.hotel_id == hotel.id).all()
        for image in check_image:
            image_data = {
                'image_id': image.id,
                'image': image.image
            }
            data.append(image_data)
        check_offers = db.query(models.Create_Offer).filter(models.Create_Offer.hotel_id == hotel.id).order_by(models.Create_Offer.created_at.desc()).limit(2)
        for offer in check_offers:
            offer_data = {
                'id': offer.id,
                'name': offer.name,
                'offer_on': offer.offer_on,
                'price': offer.price,
                'closing': offer.closing,
                'discription': offer.discription,
                'offer_image': offer.offer_image,
                'discount': offer.discount,
                'is_unlimited': offer.is_unlimited,
                'created_at': offer.created_at,
            }
            offers.append(offer_data)

    return {"status": True,"message":"Success","body":response}


@router.get('/get_all_hotel_without_login', status_code=status.HTTP_200_OK)
def get_all_hotel(db: Session = Depends(get_db)):
    hotels = db.query(models.Hotel_Sign_up).order_by(models.Hotel_Sign_up.created_at.desc()).all()

    response = []
    for hotel in hotels:
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        rating_total = sum(rating.rating for rating in ratings) if ratings else 0
        rating_average = rating_total / len(ratings) if ratings else 0
        data = []
        offers = []
        respons = {
            'id': hotel.id,
            'hotel_name': hotel.name,
            'hotel_discription': hotel.discription,
            'email': hotel.email,
            'gallery': data, 
            'longitude': hotel.longitude,
            'latitude':hotel.latitude,
            'phone_number': hotel.phone_number,
            'hotel_pic': hotel.hotel_image_url,
            'hotel_logo': hotel.logo_image_url,
            'upgrade': hotel.is_pro,
            'favorite' : False,
            'rate_this_hotel': False,
            'rating_total': rating_total,
            'rating_average': round(rating_average, 1),
            'hotel_offers': offers
        }
        response.append(respons)

        check_image = db.query(models.Hotel_Gallery_Image).filter(models.Hotel_Gallery_Image.hotel_id == hotel.id).all()
        for image in check_image:
            image_data = {
                'image_id': image.id,
                'image': image.image
            }
            data.append(image_data)
        check_offers = db.query(models.Create_Offer).filter(models.Create_Offer.hotel_id == hotel.id).order_by(models.Create_Offer.created_at.desc()).limit(2)
        for offer in check_offers:
            offer_data = {
                'id': offer.id,
                'name': offer.name,
                'offer_on': offer.offer_on,
                'price': offer.price,
                'closing': offer.closing,
                'discription': offer.discription,
                'offer_image': offer.offer_image,
                'discount': offer.discount,
                'is_unlimited': offer.is_unlimited,
                'created_at': offer.created_at,
            }
            offers.append(offer_data)

    return {"status": True,"message":"Success","body":response}



@router.get('/get_resturant_offer', status_code=status.HTTP_200_OK)
def get_restaurant_offer(hotel_id: str, db: Session = Depends(get_db)):

    
    check = db.query(models.Create_Offer).filter(models.Create_Offer.hotel_id == hotel_id).order_by(models.Create_Offer.created_at.desc()).all()

    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "hotel does not currently have any offers available."})

    resp = []
    for usermodel in check:
        
        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "hotel does not currently have any offers available."})
        
        # tz = pytz.timezone('Europe/Athens')
        # remaining_time = usermodel.closing.astimezone(tz) - datetime.now(tz)
        # days, seconds = divmod(remaining_time.seconds, 86400)
        # hours, seconds = divmod(seconds, 3600)
        # minutes, seconds = divmod(seconds, 60)
        # remaining_time_str = f"{days} days {hours} hours {minutes} minutes"

        offer_data = {
            'id': usermodel.id,
            'name': usermodel.name,
            'offer_on': usermodel.offer_on,
            'price': usermodel.price,
            'closing': usermodel.closing,
            'discription': usermodel.discription,
            'offer_image': usermodel.offer_image,
            'discount': usermodel.discount,
            # 'end_date': remaining_time_str,
            # 'last_scan': usermodel2,
            'is_unlimited': usermodel.is_unlimited,
            'created_at': usermodel.created_at,
        }
        resp.append(offer_data)

    return {"status": True, "message": "Success" ,"body": resp}

@router.get('/get_one_offer', status_code=status.HTTP_200_OK)
def get_one_offer(offer_id: str, db: Session = Depends(get_db)):

    usermodel = db.query(models.Create_Offer).filter(models.Create_Offer.id == offer_id).first()

    if not usermodel:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Hotel does not currently have any offers available."})
    

    # tz = pytz.timezone('Europe/Athens')
    # remaining_time = usermodel.closing.astimezone(tz) - datetime.now(tz)
    # days, seconds = divmod(remaining_time.seconds, 86400)
    # hours, seconds = divmod(seconds, 3600)
    # minutes, seconds = divmod(seconds, 60)
    # remaining_time_str = f"{days} days {hours} hours {minutes} minutes"

    offer_data = {
            'id': usermodel.id,
            'name': usermodel.name,
            'offer_on': usermodel.offer_on,
            'price': usermodel.price,
            'closing': usermodel.closing,
            'discription': usermodel.discription,
            'offer_image': usermodel.offer_image,
            'discount': usermodel.discount,
            # 'end_date': remaining_time_str,
            # 'last_scan': usermodel2,
            'is_unlimited': usermodel.is_unlimited,
            'created_at': usermodel.created_at,

        }

    return {"status": True, "message": "Success" ,"body": offer_data}


@router.get('/get_resturant_menu', status_code=status.HTTP_200_OK)
def get_resturant_menu(hotel_id: str, category_id: str , db: Session = Depends(get_db)):

    check = db.query(models.CreateMenu).filter(models.CreateMenu.hotel_id == hotel_id,
                                               models.CreateMenu.category_id == category_id).order_by(models.CreateMenu.created_at.desc()).all()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"Menu has not been added yet."})
    
    resp = []
    for test in check:
        usermodel = db.query(models.CreateMenu).filter(models.CreateMenu.id == test.id).first()
        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Hotel does not possess a menu"})
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
    




@router.get('/get_resturant_event', status_code=status.HTTP_200_OK)
def get_resturant_event(hotel_id: str, db: Session = Depends(get_db)):

    check = db.query(models.Create_Event).filter(models.Create_Event.hotel_id == hotel_id,
                                                 models.Create_Event.is_active == False).order_by(models.Create_Event.created_at.desc()).all()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Hotel does not currently have any events taking place"})
    
    resp = []
    for test in check:
        usermodel = db.query(models.Create_Event).filter(models.Create_Event.id == test.id).first()
        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Hotel does not currently have any events taking place"})
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



@router.get('/get_all_category', status_code=status.HTTP_200_OK)
def get_category(db: Session = Depends(get_db)):
    check = db.query(models.Create_category).order_by(models.Create_category.id.desc()).all()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "This id is not exist"})
    resp = []
    for test in check:
        usermodel = db.query(models.Create_category).filter(models.Create_category.id == test.id).first()
        if not usermodel:
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "Hotel does not currently have any events taking place."})
        offer_data = {
            'id': usermodel.id,
            'category_name': usermodel.category_name,
            'category_image': usermodel.category_image,
            'created_at': usermodel.created_at,
        }
    
        resp.append(offer_data)

    return {"status": True, "message": "Success" ,"body": resp}


@router.get('/get_favorite_hotel', status_code=status.HTTP_200_OK)
def get_favorite_hotel(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user)):

    get = db.query(models.Favorite_Hotel).filter(models.Favorite_Hotel.user_id == current_user.id).order_by(models.Favorite_Hotel.created_at.desc()).all()

    response = []
    for hotel in get:
        get_rating = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id,
                                                    models.Rating.user_id == current_user.id).first()
        if get_rating:
            usermodel4 = True
        else:
            usermodel4 = False
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        get_favorite = db.query(models.Favorite_Hotel).filter(models.Favorite_Hotel.hotel_id == hotel.id,
                                                              models.Favorite_Hotel.user_id == current_user.id).first()
        if get_favorite:
            usermodel3 = True
        else:
            usermodel3 = False
        ratings = db.query(models.Rating).filter(models.Rating.hotel_id == hotel.id).all()
        rating_total = sum(rating.rating for rating in ratings) if ratings else 0
        rating_average = rating_total / len(ratings) if ratings else 0
        check = db.query(models.Hotel_Sign_up).filter(models.Hotel_Sign_up.id == hotel.hotel_id).first()
        data = []
        respons = {
            'id': check.id,
            'hotel_name': check.name,
            'email': check.email,
            'hotel_discription': check.discription,
            'gallery': data, 
            'longitude': check.longitude,
            'latitude':check.latitude,
            'phone_number': check.phone_number,
            'hotel_pic': check.hotel_image_url,
            'hotel_logo': check.logo_image_url,
            'upgrade': check.is_pro,
            'favorite' : usermodel3,
            'rate_this_hotel': usermodel4,
            'rating_total': rating_total,
            'rating_average': round(rating_average, 1)
        }
        response.append(respons)

        check_image = db.query(models.Hotel_Gallery_Image).filter(models.Hotel_Gallery_Image.hotel_id == hotel.id).all()
        for image in check_image:
            image_data = {
                'image_id': image.id,
                'image': image.image
            }
            data.append(image_data)

    return {"status": True,"message":"Success","body":response}



@router.get("/get_offer", status_code=status.HTTP_200_OK)
def generate_qr_code(offer_id: str, current_user: int = Depends(oauth2.get_current_user) ):


    if current_user.is_verify == False:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                            content={"status": False, "message": "Please, verify your email to avail this offers"})

    res = {
        "user": str(current_user.id),
            "offer_id": offer_id
              }

    data = res
    data = str(data)
    qr = qrcode.QRCode(version=1, box_size=5, border=5)

    qr.add_data(data)

    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_bytes = buffer.getvalue()

    return Response(content= image_bytes, media_type="image/png")

@router.get('/get_one_event', status_code=status.HTTP_200_OK)
def get_one_event( event_id: str, db: Session = Depends(get_db)):

    check = db.query(models.Create_Event).filter(models.Create_Event.id == event_id,
                                                 models.Create_Event.is_active == False).first()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status": False, "message": "This ID is not exist"})

    offer_data = {
            'id': check.id,
            'event_name': check.event_name,
            'event_time': check.event_time,
            'event_end_time': check.event_end_time,
            'event_image_vedio': check.event_image_vedio,
            'event_date': check.event_date,
            'longitude':check.longitude,
            'latitude':check.latitude,
            'event_discription': check.discription,
            'is_active': check.is_active
    }

    return {"status": True, "message": "Success" ,"body": offer_data}

@router.get('/get_one_menu', status_code=status.HTTP_200_OK)
def get_one_menu(category_id: str , menu_id: str , db: Session = Depends(get_db)):

    check = db.query(models.CreateMenu).filter(models.CreateMenu.category_id == category_id,
                                               models.CreateMenu.id == menu_id).first()
    if not check:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND,
                            content={"status":False, "message":"Menu has not been added yet."})
    
    usermodel1 = db.query(models.Create_category).filter(models.Create_category.id == check.category_id).first()

    offer_data = {
            'id': check.id,
            'menu_name': check.menu_name,
            'menu_image': check.menu_image,
            'price': check.price,
            'discription': check.discription,
            'category_name': usermodel1.category_name,
            'category_image': usermodel1.category_image
        }
    return {"status": True, "message": "Success" ,"body": offer_data}


@router.get('/get_category_by_hotel_id', status_code=status.HTTP_200_OK)
def get_category_by_hotel_id(hotel_id: str , db: Session = Depends(get_db)):

    check = db.query(models.Create_category).all()

    resp = [] 
    for category in check:
        check_list = []
        data = {
            'category_id': category.id,
            'category_name':category.category_name,
            'category_image':category.category_image,
            'hotel_menu': check_list
        }
        resp.append(data)
        
        check_menu = db.query(models.CreateMenu).filter(models.CreateMenu.hotel_id == hotel_id,
                                                        models.CreateMenu.category_id == category.id).all()
        
        for menu in check_menu:
            data2 = {
            'id': menu.id,
            'menu_name': menu.menu_name,
            'menu_image': menu.menu_image,
            'price': menu.price,
            'discription': menu.discription,
            }
            check_list.append(data2)
        
    return {'status': True, 'message': 'success', 'body': resp}