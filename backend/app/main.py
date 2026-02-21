from fastapi import FastAPI
from .database import engine, Base
from . import models  # This is IMPORTANT to register models

app = FastAPI()

# Create tables in database
Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "SecureKYC Backend Running Successfully"}