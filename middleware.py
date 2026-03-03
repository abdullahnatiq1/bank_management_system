from fastapi import Request, HTTPException
from model import User
from db import engine
from utils import verifyToken
from sqlmodel import Session, select

publicRoutes = ["/auth/signup","/auth/signin", "/docs", "/openapi.json"]

async def authMiddleware(request : Request):
    token = request.headers.get("Authorization")

    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail={"message" : "Token missing. Ivalid token"})
    token = token.split(" ")[1]

    payload = verifyToken(token)
    if not payload:
        raise HTTPException(status_code = 401, detail = {"message" : "Invalid or Expired token"})
    
    uuid = payload.get("sub")

    with Session(engine) as session:
        user = session.exec(select(User).where(User.uuid == uuid)).first()

    if not user:
        raise HTTPException(status_code = 401, detail = {"message" : "User not found"})
    
    return user
