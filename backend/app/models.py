from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)


class KYC(Base):
    __tablename__ = "kyc_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    aadhaar_number = Column(String, nullable=False)
    district = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    risk_score = Column(Integer)
    status = Column(String)
    submission_date = Column(DateTime(timezone=True), server_default=func.now())
    attempt_number = Column(Integer, default=1, nullable=False)
    ocr_aadhaar_found = Column(Boolean, default=False, nullable=False)
    ocr_name_found = Column(Boolean, default=False, nullable=False)
    ocr_flags = Column(String)
    face_detected = Column(Boolean, default=False, nullable=False)