from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from .security import SECRET_KEY, ALGORITHM
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .security import hash_password, verify_password, create_access_token
from . import models
from .uidai_risk import get_district_risk_score  # ← UIDAI Integration

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

    existing_user = db.query(models.User).filter(
        models.User.email == email
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered"
        )

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

    user = db.query(models.User).filter(
        models.User.email == email
    ).first()

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


# ---------------- KYC SUBMISSION ----------------
@app.post("/kyc/submit")
def submit_kyc(
    name: str,
    aadhaar_number: str,
    district: str,
    age: int,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    risk_score = 0
    reasons = []

    # Rule 0 — Name validation
    if len(name.strip()) < 3:
        risk_score += 40
        reasons.append("Invalid name - too short")

    if not name.replace(" ", "").isalpha():
        risk_score += 40
        reasons.append("Invalid name - contains numbers or symbols")

    # Rule 1 — Aadhaar must be 12 digits
    if len(aadhaar_number) != 12 or not aadhaar_number.isdigit():
        risk_score += 40
        reasons.append("Invalid Aadhaar format")

    # Rule 2 — Underage check
    if age < 18:
        risk_score += 30
        reasons.append("Applicant is underage")

    # Rule 3 — District-Aadhaar prefix check
    district_pattern = {
        "Chennai": "11",
        "Mumbai": "22",
        "Delhi": "33"
    }

    expected_prefix = district_pattern.get(district)

    if expected_prefix and not aadhaar_number.startswith(expected_prefix):
        risk_score += 30
        reasons.append("District-Aadhaar mismatch")

    # Rule 4 — UIDAI Geographic Risk (Real Government Data)
    uidai_score = get_district_risk_score(district)
    if uidai_score > 0:
        risk_score += uidai_score
        reasons.append("High risk district based on UIDAI enrollment data")

    # ---------------- DECISION ENGINE ----------------
    if risk_score >= 70:
        status = "REJECTED"
    elif risk_score >= 40:
        status = "REVIEW"
    else:
        status = "APPROVED"

    # ---------------- SAVE TO DATABASE ----------------
    kyc_record = models.KYC(
        user_id=current_user,
        name=name,
        aadhaar_number=aadhaar_number,
        district=district,
        age=age,
        risk_score=risk_score,
        status=status
    )

    db.add(kyc_record)
    db.commit()
    db.refresh(kyc_record)

    return {
        "verification_status": status,
        "risk_score": risk_score,
        "reasons": reasons,
        "uidai_district_risk": uidai_score
    }