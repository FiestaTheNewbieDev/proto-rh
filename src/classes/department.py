from sqlalchemy import Column, Integer, String, UniqueConstraint
from pydantic import BaseModel
from base_controller import get_base

# Get the Base instance from base_controller
Base = get_base()


class Departement(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)


class UserDepartment(Base):
    __tablename__ = 'user_department'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer)
    department_id = Column(Integer)
    __table_args__ = (UniqueConstraint('user_id', 'department_id',
                                       name='Unique'),)


class AddUserToDepartment(BaseModel):
    user_ids: list[int]


class RemoveUserFromDepartment(BaseModel):
    user_ids: list[int]
