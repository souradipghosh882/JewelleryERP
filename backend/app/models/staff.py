import enum
import re
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime,
    Text, Enum as SAEnum, ForeignKey, Date, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.db.session import Base


class StaffRole(str, enum.Enum):
    OWNER = "owner"
    MANAGER = "manager"
    SALESMAN = "salesman"
    ACCOUNTANT = "accountant"
    TAGGER = "tagger"


class Staff(Base):
    __tablename__ = "staff"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_code = Column(String(20), unique=True, nullable=False)  # STF-MMYY-NNNN
    name = Column(String(100), nullable=False)
    phone = Column(String(15), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    role = Column(SAEnum(StaffRole), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    joined_date = Column(Date, nullable=False)
    aadhaar_number = Column(String(12), nullable=True)  # stored encrypted
    address = Column(Text, nullable=True)
    photo_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    attendance_logs = relationship("StaffAttendanceLog", back_populates="staff")

    @staticmethod
    def generate_staff_code(joined_date: datetime, sequence: int) -> str:
        mmyy = joined_date.strftime("%m%y")
        return f"STF-{mmyy}-{sequence:04d}"


class StaffAttendanceLog(Base):
    __tablename__ = "staff_attendance_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    staff_id = Column(UUID(as_uuid=True), ForeignKey("staff.id"), nullable=False)
    log_time = Column(DateTime, nullable=False)
    log_type = Column(String(10), nullable=False)  # "entry" or "exit"
    session = Column(String(20), nullable=False)   # "morning" or "afternoon"
    qr_code = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    staff = relationship("Staff", back_populates="attendance_logs")
