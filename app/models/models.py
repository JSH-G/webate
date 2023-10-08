import datetime
from datetime import time
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.orm import relationship
from ..database import Base
from sqlalchemy import TIMESTAMP, Column, ForeignKey, String, Boolean, func, DateTime, Time, Date, Numeric, Float
from sqlalchemy.sql.expression import  text


class User_Sign_Up(Base):
    __tablename__ = "user_signup"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    device_token = Column(String, nullable=False)
    is_active = Column(Boolean, server_default='FALSE', nullable=False)
    is_verify = Column(Boolean, server_default='FALSE', nullable=False)
    is_online = Column(Boolean, server_default='FALSE', nullable=False)
    is_delete = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class Hotel_Sign_up(Base):
    __tablename__ = "hotel_signup"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)
    phone_number = Column(String, nullable = True)
    discription = Column(String, nullable=True)
    postal_code = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    hotel_image_url = Column(String, nullable=True, server_default='https://codedeskstudio.s3.ap-northeast-1.amazonaws.com/a@a_com.jpg')
    logo_image_url = Column(String, nullable=True, server_default='https://codedeskstudio.s3.ap-northeast-1.amazonaws.com/a@a_com.jpg')
    device_token = Column(String, nullable=True)
    longitude = Column(String, nullable=True, server_default='23.727539')
    latitude = Column(String, nullable=True, server_default='37.983810')
    opening = Column(String, nullable=True,server_default='---')
    closing = Column(String, nullable=True,server_default='---')
    is_top = Column(Boolean, server_default='FALSE', nullable=False)
    is_active = Column(Boolean, server_default='FALSE', nullable=False)
    is_verify = Column(Boolean, server_default='FALSE', nullable=False)
    is_online = Column(Boolean, server_default='FALSE', nullable=False)
    is_delete = Column(Boolean, server_default='FALSE', nullable=False)
    is_pro = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class Admin_Sign_Up(Base):
    __tablename__ = "admin_signup"

    id = Column(UUID(as_uuid=True), primary_key= True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    device_token = Column(String, nullable=True)
    admin_image = Column(String, nullable=True, server_default='https://codedeskstudio.s3.ap-northeast-1.amazonaws.com/a@a_com.jpg')
    is_online = Column(Boolean, server_default='FALSE', nullable=False)
    is_active = Column(Boolean, server_default='FALSE', nullable=False)
    is_verify = Column(Boolean, server_default='FALSE', nullable=False)
    login_type = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class Create_Offer(Base):
    __tablename__ = "create_offer"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    offer_on = Column(String, nullable=True)
    offer_image = Column(String, nullable=True, server_default='https://codedeskstudio.s3.ap-northeast-1.amazonaws.com/a@a_com.jpg')
    opening = Column(DateTime, nullable=True)
    closing = Column(DateTime, nullable=True)
    discription = Column(String, nullable=True)
    discount = Column(String, nullable=True)
    price = Column(String, nullable=True)
    hotel_id = Column(UUID(as_uuid=True), ForeignKey("hotel_signup.id", ondelete="CASCADE"), default=uuid.uuid4)
    is_active = Column(Boolean, server_default='FALSE', nullable=False)
    is_unlimited = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    offer_owner = relationship("Hotel_Sign_up")


class Create_Event(Base):
    __tablename__ = "create_event"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_name = Column(String, nullable=True)
    event_time = Column(Time(timezone=True), nullable= True)
    event_end_time = Column(Time(timezone=True), nullable= True)
    event_image_vedio = Column(String, nullable=True, server_default='https://codedeskstudio.s3.ap-northeast-1.amazonaws.com/a@a_com.jpg')
    event_date = Column(Date, nullable = True)
    longitude = Column(String, nullable=True, server_default='23.727539')
    latitude = Column(String, nullable=True, server_default='37.983810')
    discription = Column(String, nullable=True)
    hotel_id = Column(UUID(as_uuid=True), ForeignKey("hotel_signup.id", ondelete="CASCADE"), default=uuid.uuid4)
    is_active = Column(Boolean, server_default='FALSE', nullable=False)
    is_verify = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    event_owner = relationship("Hotel_Sign_up")


class Create_category(Base):
    __tablename__ = "create_category"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name = Column(String, nullable=True)
    category_image = Column(String, nullable = True, server_default='https://codedeskstudio.s3.ap-northeast-1.amazonaws.com/a@a_com.jpg')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))


class CreateMenu(Base):
    __tablename__ = "create_menu"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    menu_name = Column(String, nullable=True)
    price = Column(String, nullable=True)
    menu_image = Column(String, nullable = True, server_default='https://codedeskstudio.s3.ap-northeast-1.amazonaws.com/a@a_com.jpg')
    discription = Column(String, nullable=True)
    hotel_id = Column(UUID(as_uuid=True), ForeignKey("hotel_signup.id", ondelete="CASCADE"), default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("create_category.id", ondelete="CASCADE"), default=uuid.uuid4)
    is_active = Column(Boolean, server_default='FALSE', nullable=False)
    is_pro = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    update_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    category = relationship("Create_category")

class Rating(Base):
    __tablename__ = "ratings"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hotel_id = Column(UUID(as_uuid=True), ForeignKey("hotel_signup.id", ondelete="CASCADE"), default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_signup.id", ondelete="CASCADE"), default=uuid.uuid4)
    rating = Column(Float, nullable=True)
    comment = Column(String, nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    Raiting_Review = relationship("Hotel_Sign_up")
    Owner_Name = relationship("User_Sign_Up")

class Favorite_Hotel(Base):
    __tablename__ = "favorite_hotel"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hotel_id = Column(UUID(as_uuid=True), ForeignKey("hotel_signup.id", ondelete="CASCADE"), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_signup.id", ondelete="CASCADE"), primary_key=True, default=uuid.uuid4)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    Hotel_Name = relationship("Hotel_Sign_up")

class Offer_Scan(Base):
    __tablename__ = "offer_scan"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_signup.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    offer_id = Column(UUID(as_uuid=True), ForeignKey("create_offer.id", ondelete="CASCADE"),primary_key=True, nullable=False)
    hotel_id = Column(UUID(as_uuid=True), ForeignKey("hotel_signup.id", ondelete="CASCADE"), primary_key=True, default=uuid.uuid4)
    scan_time = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

    Hotel_Data = relationship("Hotel_Sign_up")
    Offer_Data = relationship("Create_Offer")

class Contact_Us(Base):
    __tablename__ = "contact_us"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    budget = Column(String, nullable= True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

class Hotel_Gallery_Image(Base):
    __tablename__ = "hotel_gallery_image"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hotel_id = Column(UUID(as_uuid=True), ForeignKey("hotel_signup.id", ondelete="CASCADE"), primary_key=True, default=uuid.uuid4)
    image = Column(String, nullable=True, server_default='https://codedeskstudio.s3.ap-northeast-1.amazonaws.com/2023-04-06_15_23_29_299687no-profile-picture-icon_webp.jpg')
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))




# class Notification(Base):

#     __tablename__ = "notification"

#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     notify_message = Column(String, nullable=True)
#     notify_purpose_id = Column(String, nullable=True)
#     notify_type = Column(String, nullable=True)
#     notify_send_id = Column(String, nullable=True)
#     notify_receive_id = Column(UUID(as_uuid=True), ForeignKey("user_signup.id", ondelete= "CASCADE"), default= uuid.uuid4)
#     created_at = Column(TIMESTAMP(timezone=True), nullable = False, server_default=text('now()'))