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

from fastapi import UploadFile, File
from pypdf import PdfReader
import io

from vectorstore import store_chunks

@app.post("/upload-report")
async def upload_report(file: UploadFile = File(...)):
    contents = await file.read()
    pdf_reader = PdfReader(io.BytesIO(contents))
    
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    
    chunks = chunk_text(extracted_text)
    stored_count = store_chunks(chunks, report_id=file.filename)
    
    return {
        "filename": file.filename,
        "pages": len(pdf_reader.pages),
        "num_chunks": len(chunks),
        "stored_in_chroma": stored_count
    }
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text: str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    return splitter.split_text(text)
from summarizer import summarize_report

@app.post("/summarize-report")
async def summarize_report_endpoint(file: UploadFile = File(...)):
    contents = await file.read()
    pdf_reader = PdfReader(io.BytesIO(contents))
    
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    
    chunks = chunk_text(extracted_text)
    summary = summarize_report(chunks)
    
    return {"filename": file.filename, "summary": summary}

from drug_interaction import check_drug_interactions
from pydantic import BaseModel

class DrugList(BaseModel):
    drugs: list[str]

@app.post("/check-interactions")
def check_interactions_endpoint(payload: DrugList):
    return check_drug_interactions(payload.drugs)


from medical_retrieval import store_medline_knowledge, retrieve_relevant_knowledge

class TopicRequest(BaseModel):
    term: str

@app.post("/fetch-medical-knowledge")
def fetch_medical_knowledge(payload: TopicRequest):
    stored_count = store_medline_knowledge(payload.term)
    retrieved = retrieve_relevant_knowledge(payload.term)
    return {"term": payload.term, "stored_topics": stored_count, "retrieved_content": retrieved}

from explanation_agent import generate_patient_explanation

class ExplanationRequest(BaseModel):
    summary: str
    drug_interactions: list = None
    medical_context: list = None

@app.post("/explain-to-patient")
def explain_to_patient(payload: ExplanationRequest):
    explanation = generate_patient_explanation(
        payload.summary,
        payload.drug_interactions,
        payload.medical_context
    )
    return {"explanation": explanation}