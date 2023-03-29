from fastapi import FastAPI
from .database import engine
from .routers import user_signup, auth, hotel_signup, hotel_auth, create_offer, create_event, admin_auth, admin_signup
from .routers import category, create_menu, rating, favorite_hotel, get_hotel, offer_scan, contact_us, get_admin_side
from .models import models


models.Base.metadata.create_all(bind=engine)



app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Wellcome to We-Bate api please write end of code /docs"}

app.include_router(user_signup.router)
app.include_router(auth.router)
app.include_router(hotel_signup.router)
app.include_router(hotel_auth.router)
app.include_router(create_offer.router)
app.include_router(create_event.router)
app.include_router(admin_signup.router)
app.include_router(admin_auth.router)
app.include_router(category.router)
app.include_router(create_menu.router)
app.include_router(rating.router)
app.include_router(favorite_hotel.router)
app.include_router(get_hotel.router)
app.include_router(offer_scan.router)
app.include_router(contact_us.router)
app.include_router(get_admin_side.router)