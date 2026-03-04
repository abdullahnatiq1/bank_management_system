from fastapi import APIRouter, Depends, HTTPException
from model import User, Account, CreateaccountRequest, TransactionManagement, TransactionType, TransactionLimit
from db import getSession
from middleware import authMiddleware
from sqlmodel import Session, select
from middleware import authMiddleware
import random
from datetime import datetime, timezone, time
from sqlalchemy import func


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

@router.post("/transaction")
def transactions(data : TransactionManagement, session : Session = Depends(getSession), currentUser : User = Depends(authMiddleware)):
    
    todayStart = datetime.combine(datetime.now(timezone.utc).date(), time.min)

    history = session.exec(select(TransactionLimit).where(TransactionLimit.accountNo == data.senderAccount, TransactionLimit.timestamp >= todayStart)).all()
    
    totalSpendTody = 0
    for tx in history:
        totalSpendTody += tx.amount

    if totalSpendTody + data.amount > 5000:
        raise HTTPException(status_code = 400, detail = {"message" : "Daily limit reached"})

    sender = session.exec(select(Account).where(Account.accountNo == data.senderAccount)).first()
    receiver = session.exec(select(Account).where(Account.accountNo == data.receiverAccount)).first()

    if not sender or not receiver:
        raise HTTPException(status_code = 401, detail = {"message" : "Account not found"})

    if sender.balance < data.amount:
        raise HTTPException(status_code = 401, detail = {"message" : "Insufficiant Balance"})
    
    sender.balance -= data.amount
    receiver.balance += data.amount

    session.add(sender)
    session.add(receiver)
    session.commit()

    session.refresh(sender)

    return{"message" : "Transaction successful",
           "sender balance" : sender.balance
           }
