from fastapi import FastAPI
from database import engine
from sqlalchemy import text
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import models
import schemas
from database import engine, get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(title="MediAssist AI")


@app.get("/")
def read_root():
    return {"message": "MediAssist AI backend is running"}


@app.get("/db-check")
def db_check():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"database": "connected successfully"}
    except Exception as e:
        return {"database": "connection failed", "error": str(e)}
import models
from database import engine

models.Base.metadata.create_all(bind=engine)


from fastapi import Depends

@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_password = pwd_context.hash(user.password)
    new_user = models.User(email=user.email, password_hash=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

from datetime import datetime, timedelta
from jose import jwt

from database import engine, get_db
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

from fastapi import HTTPException

@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}