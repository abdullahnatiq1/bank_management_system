from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from db import getSession
from model import User, SignupRequest, SigninRequest
import bcrypt
from utils import createToken, verifyToken
from middleware import authMiddleware


router = APIRouter(prefix="/auth",tags=["authentication"])

@router.get("/me")
def authenticated(currentUser : User = Depends(authMiddleware)):
    return{"user" : currentUser}


@router.post("/signup")
def signUp(SignupRequest : SignupRequest, session : Session = Depends(getSession)):
    existingUser = session.exec(select(User).where(User.email == SignupRequest.email)).first()
    if existingUser:
        return{"message" : "User already exists with this email. Please Signin"}
    
    hashedpassword = bcrypt.hashpw(SignupRequest.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    newUser = User(username = SignupRequest.username, dob = SignupRequest.dob, email = SignupRequest.email, phoneNo = SignupRequest.phoneNo, password = hashedpassword, address = SignupRequest.address)
    session.add(newUser)
    session.commit()
    session.refresh(newUser)

    return{"message" : "User created successfully"}

@router.post("/signin")
def signIn(SigninRequest : SigninRequest, session : Session = Depends(getSession)):
    user = session.exec(select(User).where(User.email == SigninRequest.email)).first()
    if not user:
        return{"message" : "Email not found"}
    
    passwordMatch = bcrypt.checkpw(SigninRequest.password.encode('utf-8'), user.password.encode('utf-8'))
    if not passwordMatch:
        return{"message" : "Invalid password"}
    
    token = createToken(data = {"sub" : user.uuid})
    return {
        "message" : "login Successful",
        "token" : token
    }