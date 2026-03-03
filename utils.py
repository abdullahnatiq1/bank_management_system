from jose import jwt 
from datetime import timedelta, datetime

SECRET_KEY = "your_secret_key"
algorithm = "HS256"

def createToken(data : dict):
    expire = datetime.utcnow() + timedelta(hours = 24)
    data.update({"exp" : expire})
    token = jwt.encode(data, SECRET_KEY, algorithm=algorithm)
    return token

def verifyToken(token : str):
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
