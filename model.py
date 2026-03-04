from sqlmodel import SQLModel, Field, Column, Integer, Relationship, BigInteger
from typing import Optional, List
import uuid
from datetime import datetime, timezone
from enum import Enum
import sqlalchemy as sa


class User(SQLModel, table = True):
    __tablename__ = "users"
    id : Optional[int] = Field(sa_column = Column(Integer, autoincrement = True, unique = True, primary_key = True))
    uuid : str = Field(default_factory = lambda : str(uuid.uuid4()), unique = True)
    username : str 
    dob : str
    email : str = Field(unique = True)
    phoneNo : int = Field(unique = True)
    password : str
    address : str

    accounts : List["Account"] = Relationship(back_populates = "owner")


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

class Account(SQLModel, table = True): 
    __tablename__ = "accounts"
    accountTitle : str = Field(default = None)
    id : Optional[int] = Field(default = None, primary_key = True)
    accountUUID : str = Field(default_factory = lambda : str(uuid.uuid4()), unique = True)
    accountNo : int = Field(unique = True, index = True, sa_type = BigInteger)
    accountType : str = Field(default = "SAVING")
    balance : float = Field(default = 0.0)
    status : bool = Field(default = True)
    createdAt : datetime = Field(default_factory = datetime.utcnow)

    userUUID : str = Field(foreign_key = "users.uuid")

    owner : Optional[User] = Relationship(back_populates = "accounts")

    
class CreateaccountRequest(SQLModel):
    id : int
    AccountUUID : str
    accountNo : int
    accountType : str
    balance : float
    status : bool 
    createdAt : datetime
    userUUID : str
    accountTitle : str

class TransactionManagement(SQLModel):
    senderAccount : int
    receiverAccount : int
    amount : float


class TransactionType(str , Enum):
    DEPOSIT : "DEPOSIT"
    WITHDRAW : "WITHDRAW"
    TRANSFER : "TRANSFER"


class TransactionLimit(SQLModel, table = True):
    __tablename__ = "transactions"
    id : Optional[int] = Field(default = None, primary_key = True)
    accountNo : int
    receiverAccount : Optional[int] = None   # only used if transfer is called
    amount : float
    type : TransactionType = Field(sa_column = sa.Column(sa.Enum(TransactionType, name = "transaction_type_enum")))
    timestamp : datetime = Field(default_factory = lambda : datetime.now(timezone.utc))

