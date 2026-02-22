from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from .security import SECRET_KEY, ALGORITHM
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .security import hash_password, verify_password, create_access_token
from . import models

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# ---------------- DB DEPENDENCY ----------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- JWT SECURITY ----------------
security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return user_id

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# ---------------- ROOT ----------------
@app.get("/")
def root():
    return {"message": "SecureKYC Backend Running Successfully"}


# ---------------- REGISTER ----------------
@app.post("/register")
def register_user(email: str, password: str, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(password)

    new_user = models.User(
        email=email,
        hashed_password=hashed_pwd
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


# ---------------- LOGIN ----------------
@app.post("/login")
def login_user(email: str, password: str, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.email == email).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# ---------------- PROTECTED ROUTE ----------------
@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_id": current_user
    }