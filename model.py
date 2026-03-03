from sqlmodel import SQLModel, Field, Column, Integer
from typing import Optional
import uuid


class User(SQLModel, table = True):
    __tablename__ = "users"
    id : Optional[int] = Field(sa_column = Column(Integer, autoincrement = True, unique = True, primary_key = True))
    uuid : str = Field(default_factory = lambda : str(uuid.uuid4()))
    username : str 
    dob : str
    email : str = Field(unique = True)
    phoneNo : int = Field(unique = True)
    password : str
    address : str


class SignupRequest(SQLModel):
    username : str
    dob : str
    email : str
    phoneNo : int
    password : str
    address : str

class SigninRequest(SQLModel):
    email : str
    password : str