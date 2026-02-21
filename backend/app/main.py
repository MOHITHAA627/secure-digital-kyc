from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .security import hash_password
from . import models

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def root():
    return {"message": "SecureKYC Backend Running Successfully"}


@app.post("/register")
def register_user(email: str, password: str, db: Session = Depends(get_db)):

    # Check if user already exists
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_pwd = hash_password(password)

    # Create user
    new_user = models.User(
        email=email,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}