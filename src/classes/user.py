from datetime import date as _date
from sqlalchemy import Column, Integer, String, Date, JSON
from pydantic import BaseModel

from base_controller import get_base

# Get the Base instance from base_controller
Base = get_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String)
    password = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    birthday_date = Column(String)
    adress = Column(String)
    postal_code = Column(String)
    age = Column(Integer)
    meta = Column(JSON)
    registration_date = Column(Date)
    token = Column(String)
    role = Column(String)


class CreateUser(BaseModel):
    email: str
    password: str
    firstname: str
    lastname: str
    birthday_date: _date
    adress: str
    postal_code: str


class Connect(BaseModel):
    email: str
    password: str


class UpdateUser(BaseModel):
    id: int = None
    email: str = None
    firstname: str = None
    lastname: str = None
    birthday_date: _date = None
    adress: str = None
    postal_code: str = None
    role: str = None


class UpdatePassword(BaseModel):
    email: str
    password: str
    new_password: str
    repeat_new_password: str
