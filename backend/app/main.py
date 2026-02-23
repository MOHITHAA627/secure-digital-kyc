from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from .security import SECRET_KEY, ALGORITHM
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .security import hash_password, verify_password, create_access_token
from . import models
from .uidai_risk import get_district_risk_score
import shutil, os, io, re, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

import pytesseract
from PIL import Image
import cv2
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


def send_kyc_email(email: str, name: str, status: str, risk_score: int, reasons: list[str]) -> None:
    sender = os.getenv("EMAIL_SENDER")
    password = os.getenv("EMAIL_PASSWORD")
    if not sender or not password or not email:
        return

    subject = "SecureKYC-AI — Your KYC Application Status"

    if status == "APPROVED":
        next_steps = "Your account is ready. Welcome!"
        status_text = "APPROVED"
    elif status == "REVIEW":
        next_steps = "Our team will contact you within 2 business days."
        status_text = "UNDER REVIEW"
    else:
        next_steps = "You may reapply after correcting the flagged issues."
        status_text = "REJECTED"

    reasons_text = "\n".join(f"- {r}" for r in reasons) if reasons else "No issues were flagged."

    body = f"""Hello {name},

Your KYC application status: {status_text}

Risk score: {risk_score}

Reasons flagged:
{reasons_text}

Next steps:
{next_steps}

Thank you,
SecureKYC-AI"""

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
    except Exception:
        # Fail silently so email problems don't break API
        pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.get("/")
def root():
    return {"message": "SecureKYC Backend Running Successfully"}

@app.post("/register")
def register_user(email: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = hash_password(password)
    new_user = models.User(email=email, hashed_password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

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
        "token_type": "bearer",
        "is_admin": bool(user.is_admin),
    }

@app.get("/protected")
def protected_route(current_user: str = Depends(get_current_user)):
    return {"message": "You are authenticated", "user_id": current_user}

@app.post("/kyc/upload")
def upload_document(
    file: UploadFile = File(...),
    name: str = "",
    current_user: str = Depends(get_current_user)
):
    allowed_extensions = [".jpg", ".jpeg", ".png", ".pdf"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPG, PNG, PDF allowed.")

    allowed_mimes = ["image/jpeg", "image/png", "image/jpg", "application/pdf"]
    if file.content_type not in allowed_mimes:
        raise HTTPException(status_code=400, detail="Invalid file format detected.")

    content = file.file.read()

    if len(content) > 2 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 2MB.")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="File is empty or corrupted.")

    jpeg_magic = content[:3] == b'\xff\xd8\xff'
    png_magic = content[:8] == b'\x89PNG\r\n\x1a\n'
    pdf_magic = content[:4] == b'%PDF'

    if ext in [".jpg", ".jpeg"] and not jpeg_magic:
        raise HTTPException(status_code=400, detail="File is not a valid JPEG image.")
    if ext == ".png" and not png_magic:
        raise HTTPException(status_code=400, detail="File is not a valid PNG image.")
    if ext == ".pdf" and not pdf_magic:
        raise HTTPException(status_code=400, detail="File is not a valid PDF.")

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = f"{upload_dir}/{current_user}_{file.filename}"

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    ocr_text = ""
    aadhaar_found = False
    name_found = False
    flags: list[str] = []

    if ext in [".jpg", ".jpeg", ".png"]:
        try:
            image = Image.open(io.BytesIO(content))
            ocr_text = pytesseract.image_to_string(image)
            match = re.search(r"\b\d{12}\b", ocr_text)
            if match:
                aadhaar_found = True
            if name:
                normalized_name = name.strip().lower()
                if normalized_name in ocr_text.lower():
                    name_found = True
        except Exception:
            flags.append("OCR processing failed")
    else:
        flags.append("OCR not run for non-image document")

    if not aadhaar_found:
        flags.append("No Aadhaar number detected in document")
    if name and not name_found:
        flags.append("Name mismatch between form and document")

    face_detected = False
    face_message = "Face detection not run"
    if ext in [".jpg", ".jpeg", ".png"]:
        try:
            image_cv = cv2.imdecode(
                np.frombuffer(content, dtype="uint8"), cv2.IMREAD_COLOR  # type: ignore[name-defined]
            )
        except Exception:
            image_cv = None

        if image_cv is not None:
            gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            face_cascade = cv2.CascadeClassifier(cascade_path)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
            if len(faces) > 0:
                face_detected = True
                face_message = "Face detected in document"
            else:
                face_message = "No face detected in document - may not be a valid ID"
                flags.append("No face detected in document - may not be a valid ID")

    return {
        "message": "Document uploaded and verified successfully",
        "filename": file.filename,
        "size_kb": round(len(content) / 1024, 2),
        "format_verified": True,
        "ocr_text": ocr_text,
        "aadhaar_found": aadhaar_found,
        "name_found": name_found,
        "flags": flags,
        "face_detected": face_detected,
        "face_message": face_message,
    }

def _calculate_kyc_decision(name: str, aadhaar_number: str, district: str, age: int) -> tuple[int, str, list[str], int]:
    risk_score = 0
    reasons: list[str] = []

    if len(name.strip()) < 3:
        risk_score += 40
        reasons.append("Invalid name - too short")

    if not name.replace(" ", "").isalpha():
        risk_score += 40
        reasons.append("Invalid name - contains numbers or symbols")

    if len(aadhaar_number) != 12 or not aadhaar_number.isdigit():
        risk_score += 40
        reasons.append("Invalid Aadhaar format")

    if age < 18:
        risk_score += 30
        reasons.append("Applicant is underage")

    district_pattern = {
        "Chennai": "11",
        "Mumbai": "22",
        "Delhi": "33",
    }
    expected_prefix = district_pattern.get(district)
    if expected_prefix and not aadhaar_number.startswith(expected_prefix):
        risk_score += 30
        reasons.append("District-Aadhaar mismatch")

    uidai_score = get_district_risk_score(district)
    if uidai_score == 25:
        risk_score += uidai_score
        reasons.append("High risk district based on UIDAI enrollment data")
    elif uidai_score == 15:
        risk_score += uidai_score
        reasons.append("District not in UIDAI dataset - unverified region")

    if risk_score >= 70:
        status = "REJECTED"
    elif risk_score >= 40:
        status = "REVIEW"
    else:
        status = "APPROVED"

    return risk_score, status, reasons, uidai_score


@app.post("/kyc/submit")
def submit_kyc(
    name: str,
    aadhaar_number: str,
    district: str,
    age: int,
    ocr_aadhaar_found: bool = False,
    ocr_name_found: bool = False,
    face_detected: bool = False,
    ocr_flags: str | None = None,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    risk_score, status, reasons, uidai_score = _calculate_kyc_decision(
        name=name,
        aadhaar_number=aadhaar_number,
        district=district,
        age=age,
    )

    if not ocr_aadhaar_found:
        reasons.append("OCR could not confirm Aadhaar in document")
    if not ocr_name_found:
        reasons.append("OCR could not confirm name in document")
    if not face_detected:
        reasons.append("No face confirmed in document by detector")

    kyc_record = models.KYC(
        user_id=int(current_user),
        name=name,
        aadhaar_number=aadhaar_number,
        district=district,
        age=age,
        risk_score=risk_score,
        status=status,
        ocr_aadhaar_found=ocr_aadhaar_found,
        ocr_name_found=ocr_name_found,
        ocr_flags=ocr_flags,
        face_detected=face_detected,
    )
    db.add(kyc_record)
    db.commit()
    db.refresh(kyc_record)

    user = db.query(models.User).filter(models.User.id == int(current_user)).first()
    if user:
        send_kyc_email(
            email=user.email,
            name=name,
            status=status,
            risk_score=risk_score,
            reasons=reasons,
        )

    return {
        "verification_status": status,
        "risk_score": risk_score,
        "reasons": reasons,
        "uidai_district_risk": uidai_score,
        "attempt_number": kyc_record.attempt_number,
    }


@app.get("/kyc/history")
def get_kyc_history(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    records = (
        db.query(models.KYC)
        .filter(models.KYC.user_id == int(current_user))
        .order_by(models.KYC.submission_date.desc())
        .all()
    )

    return {
        "total": len(records),
        "approved": len([r for r in records if r.status == "APPROVED"]),
        "review": len([r for r in records if r.status == "REVIEW"]),
        "rejected": len([r for r in records if r.status == "REJECTED"]),
        "records": [
            {
                "name": r.name,
                "district": r.district,
                "age": r.age,
                "risk_score": r.risk_score,
                "status": r.status,
                "attempt_number": r.attempt_number,
                "submission_date": r.submission_date.isoformat() if r.submission_date else None,
            } for r in records
        ]
    }


@app.get("/kyc/status")
def get_kyc_status(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = (
        db.query(models.KYC)
        .filter(models.KYC.user_id == int(current_user))
        .order_by(models.KYC.submission_date.desc())
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="No KYC record found")
    return {
        "status": record.status,
        "attempt_number": record.attempt_number,
    }


@app.post("/kyc/resubmit")
def resubmit_kyc(
    name: str,
    aadhaar_number: str,
    district: str,
    age: int,
    ocr_aadhaar_found: bool = False,
    ocr_name_found: bool = False,
    face_detected: bool = False,
    ocr_flags: str | None = None,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = int(current_user)

    rejected_records = (
        db.query(models.KYC)
        .filter(models.KYC.user_id == user_id, models.KYC.status == "REJECTED")
        .order_by(models.KYC.submission_date.desc())
        .all()
    )

    if len(rejected_records) >= 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum resubmission attempts reached",
        )

    latest_rejected = rejected_records[0] if rejected_records else None

    risk_score, status, reasons, uidai_score = _calculate_kyc_decision(
        name=name,
        aadhaar_number=aadhaar_number,
        district=district,
        age=age,
    )

    if not ocr_aadhaar_found:
        reasons.append("OCR could not confirm Aadhaar in document")
    if not ocr_name_found:
        reasons.append("OCR could not confirm name in document")
    if not face_detected:
        reasons.append("No face confirmed in document by detector")

    if latest_rejected:
        latest_rejected.name = name
        latest_rejected.aadhaar_number = aadhaar_number
        latest_rejected.district = district
        latest_rejected.age = age
        latest_rejected.risk_score = risk_score
        latest_rejected.status = status
        latest_rejected.submission_date = datetime.utcnow()
        latest_rejected.attempt_number = min(
            (latest_rejected.attempt_number or 1) + 1,
            3,
        )
        latest_rejected.ocr_aadhaar_found = ocr_aadhaar_found
        latest_rejected.ocr_name_found = ocr_name_found
        latest_rejected.ocr_flags = ocr_flags
        latest_rejected.face_detected = face_detected
        kyc_record = latest_rejected
    else:
        kyc_record = models.KYC(
            user_id=user_id,
            name=name,
            aadhaar_number=aadhaar_number,
            district=district,
            age=age,
            risk_score=risk_score,
            status=status,
            attempt_number=1,
            ocr_aadhaar_found=ocr_aadhaar_found,
            ocr_name_found=ocr_name_found,
            ocr_flags=ocr_flags,
            face_detected=face_detected,
        )
        db.add(kyc_record)

    db.commit()
    db.refresh(kyc_record)

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user:
        send_kyc_email(
            email=user.email,
            name=name,
            status=status,
            risk_score=risk_score,
            reasons=reasons,
        )

    return {
        "verification_status": status,
        "risk_score": risk_score,
        "reasons": reasons,
        "uidai_district_risk": uidai_score,
        "attempt_number": kyc_record.attempt_number,
    }


@app.get("/admin/all-kyc")
def get_all_kyc(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user = db.query(models.User).filter(models.User.id == int(current_user)).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")

    records = (
        db.query(models.KYC, models.User)
        .join(models.User, models.KYC.user_id == models.User.id)
        .order_by(models.KYC.submission_date.desc())
        .all()
    )

    flattened = []
    for kyc, u in records:
        flattened.append(
            {
                "email": u.email,
                "name": kyc.name,
                "district": kyc.district,
                "age": kyc.age,
                "risk_score": kyc.risk_score,
                "status": kyc.status,
                "submission_date": kyc.submission_date.isoformat() if kyc.submission_date else None,
                "attempt_number": kyc.attempt_number,
            }
        )

    return {
        "total": len(flattened),
        "approved": len([r for r in flattened if r["status"] == "APPROVED"]),
        "review": len([r for r in flattened if r["status"] == "REVIEW"]),
        "rejected": len([r for r in flattened if r["status"] == "REJECTED"]),
        "records": flattened,
    }