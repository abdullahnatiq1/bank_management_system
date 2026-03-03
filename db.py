import os
from dotenv import load_dotenv
from sqlmodel import create_engine, Session, SQLModel
from model import User


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not found in .env. Please check your configuration")

engine = create_engine(DATABASE_URL, echo = True)
def createDBandTables():
    """
    Initialize the databse scheme based on your SQLModel
    """

    SQLModel.metadata.create_all(engine)

def getSession():
    """
    Provides a Database session to your routes and ensure it closes after use
    """
    with Session(engine) as session:
        yield session
