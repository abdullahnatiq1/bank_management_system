from fastapi import APIRouter, Depends 
from model import User, Account, CreateaccountRequest
from db import getSession
from middleware import authMiddleware
from sqlmodel import Session, select
from middleware import authMiddleware
import random


router = APIRouter(prefix="/account", tags=["User Bank Account"])

@router.post("/create")
def createAccount(accountData : CreateaccountRequest, session : Session = Depends(getSession), currentUser : User = Depends(authMiddleware)):
    print(f"Creating account: {accountData.accountTitle}")
    
    generatedNo = random.randint(1000000000, 9999999999)
    
    newAccount = Account(accountTitle  = accountData.accountTitle, accountType = accountData.accountType,balance = accountData.balance, accountNo = generatedNo, userUUID = currentUser.uuid,)

    session.add(newAccount)
    session.commit()
    session.refresh(newAccount)

    return {"message" : "Account usccessfully created",
            "user account" : newAccount
            }
