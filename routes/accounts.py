from fastapi import APIRouter, Depends, HTTPException
from model import User, Account, CreateaccountRequest, TransactionManagement, TransactionType, TransactionLimit, DepositWithdrawRequest
from db import getSession
from middleware import authMiddleware
from sqlmodel import Session, select
from middleware import authMiddleware
import random
from datetime import datetime, timezone, time
from sqlalchemy import func, or_, desc


router = APIRouter(prefix="/account", tags=["User Bank Account"])

@router.post("/create")
def createAccount(accountData : CreateaccountRequest, session : Session = Depends(getSession), currentUser : User = Depends(authMiddleware)):
    print(f"Creating account: {accountData.accountTitle}")
    
    generatedNo = random.randint(1000, 9999)
    
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

    newHistory = TransactionLimit(accountNo = data.senderAccount, receiverAccount = data.receiverAccount, amount = data.amount, type = TransactionType.TRANSFER)

    session.add(sender)
    session.add(receiver)
    session.add(newHistory)
    session.commit()

    session.refresh(sender)

    return{"message" : "Transaction successful",
           "sender balance" : sender.balance
           }

@router.post("/deposit")
def depositAmount(deposit : DepositWithdrawRequest, session : Session = Depends(getSession), currentUser : User = Depends(authMiddleware)):
    account = session.exec(select(Account).where(Account.accountNo == deposit.accountNo)).first()

    if not account:
        raise HTTPException(status_code = 400, detail = "Account not found")
    
    account.balance += deposit.amount

    session.add(account)   # ye database ko ye batata hai k jo bi changes hui h usko add krdo 
    session.commit()       # ye un changes ko commit kr deta hai
    session.refresh(account)

    return {
        "message" : "Deposit successful",
        "current balance" : account.balance
    }

@router.post("/withdraw")
def withdrawAmount(withdraw : DepositWithdrawRequest, session : Session = Depends(getSession), currentUser : User = Depends(authMiddleware)):
    account = session.exec(select(Account).where(Account.accountNo == withdraw.accountNo)).first()
    
    if not account:
        raise HTTPException(status_code = 400, detail = "Account not found")
    
    account.balance -= withdraw.amount

    session.add(account)
    session.commit()
    session.refresh(account)

    return {
        "message" : "Withdraw successful",
        "remaining balance" : account.balance
    }

@router.get("/history")
def getHistory(session : Session = Depends(getSession), currentUser : User = Depends(authMiddleware)):
    account = session.exec(select(Account).where(Account.userUUID == currentUser.uuid)).first()

    if not account:
        raise HTTPException(status_code = 404, detail = "Account not found")
    
    statement = select(TransactionLimit).where(TransactionLimit.accountNo == account.accountNo).order_by(TransactionLimit.timestamp)
    history = session.exec(statement).all()

    return{
        "username" : currentUser.username,
        "account" : account.accountNo,
        "balance" : account.balance,
        "history" : history
    } 

