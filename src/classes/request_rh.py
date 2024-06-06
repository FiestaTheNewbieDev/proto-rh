from sqlalchemy import Column, Integer, String, Date, JSON, Boolean
from pydantic import BaseModel

from base_controller import get_base

# Get the Base instance from base_controller
Base = get_base()


class RequestRH(Base):
    __tablename__ = 'requests_rh'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer)
    content = Column(String)
    registration_date = Column(Date)
    visibility = Column(Boolean)
    close = Column(Boolean)
    last_action = Column(Date)
    content_history = Column(JSON)
    delete_date = Column(Date)


class CreateRequestRH(BaseModel):
    user_id: int
    content: str


class RemoveRequestRH(BaseModel):
    id: int


class UpdateRequestRH(BaseModel):
    id: int
    content: str
