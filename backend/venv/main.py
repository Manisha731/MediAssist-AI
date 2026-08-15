from fastapi import FastAPI

app = FastAPI(title="MediAssist AI")


@app.get("/")
def read_root():
    return {"message": "MediAssist AI backend is running"}