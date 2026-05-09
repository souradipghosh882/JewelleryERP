from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, field_validator
import re

from app.db.session import get_shared_db
from app.models.customer import Customer, CustomerKYCStatus
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/customers", tags=["Customers"])


class CustomerCreate(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    birth_date: Optional[date] = None
    anniversary_date: Optional[date] = None
    notes: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        if not re.match(r"^[6-9]\d{9}$", v):
            raise ValueError("Invalid Indian phone number")
        return v

    @field_validator("pan_number")
    @classmethod
    def validate_pan(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]$", v.upper()):
            raise ValueError("Invalid PAN number format")
        return v.upper() if v else None

    @field_validator("aadhaar_number")
    @classmethod
    def validate_aadhaar(cls, v: Optional[str]) -> Optional[str]:
        if v and not re.match(r"^\d{12}$", v):
            raise ValueError("Aadhaar must be 12 digits")
        return v


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    aadhaar_number: Optional[str] = None
    pan_number: Optional[str] = None
    birth_date: Optional[date] = None
    anniversary_date: Optional[date] = None
    notes: Optional[str] = None


@router.post("/", status_code=201)
def create_customer(
    payload: CustomerCreate,
    db: Session = Depends(get_shared_db),
    _=Depends(require_roles("owner", "manager", "salesman")),
):
    existing = db.query(Customer).filter(Customer.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=409, detail="Customer with this phone already exists")

    kyc = CustomerKYCStatus.NONE
    if payload.aadhaar_number and payload.pan_number:
        kyc = CustomerKYCStatus.BOTH
    elif payload.pan_number:
        kyc = CustomerKYCStatus.PAN
    elif payload.aadhaar_number:
        kyc = CustomerKYCStatus.AADHAAR

    customer = Customer(**payload.model_dump(), kyc_status=kyc)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@router.get("/")
def list_customers(
    search: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    q = db.query(Customer).filter(Customer.is_active == True)
    if search:
        q = q.filter(
            (Customer.name.ilike(f"%{search}%")) | (Customer.phone.ilike(f"%{search}%"))
        )
    return q.offset(offset).limit(limit).all()


@router.get("/{customer_id}")
def get_customer(
    customer_id: str,
    db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.patch("/{customer_id}")
def update_customer(
    customer_id: str,
    payload: CustomerUpdate,
    db: Session = Depends(get_shared_db),
    _=Depends(require_roles("owner", "manager", "salesman")),
):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(customer, field, value)

    # Recalculate KYC status
    if customer.aadhaar_number and customer.pan_number:
        customer.kyc_status = CustomerKYCStatus.BOTH
    elif customer.pan_number:
        customer.kyc_status = CustomerKYCStatus.PAN
    elif customer.aadhaar_number:
        customer.kyc_status = CustomerKYCStatus.AADHAAR
    else:
        customer.kyc_status = CustomerKYCStatus.NONE

    db.commit()
    db.refresh(customer)
    return customer
