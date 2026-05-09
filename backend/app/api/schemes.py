from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.db.session import get_shared_db
from app.models.scheme import Scheme, SchemeAccount, SchemeTransaction, SchemeType, SchemeStatus
from app.models.customer import Customer
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/schemes", tags=["Schemes"])


class SchemeCreate(BaseModel):
    name: str
    scheme_type: SchemeType
    duration_months: int
    monthly_amount: Optional[float] = None
    monthly_gold_grams: Optional[float] = None
    bonus_month: bool = True
    description: Optional[str] = None


class SchemeEnroll(BaseModel):
    scheme_id: str
    customer_id: str
    start_date: date


class SchemePayment(BaseModel):
    amount: float
    gold_grams: Optional[float] = None
    payment_date: date
    payment_mode: str
    receipt_number: Optional[str] = None
    notes: Optional[str] = None


@router.post("/", status_code=201)
def create_scheme(
    payload: SchemeCreate,
    db: Session = Depends(get_shared_db),
    _=Depends(require_roles("owner")),
):
    scheme = Scheme(**payload.model_dump())
    db.add(scheme)
    db.commit()
    db.refresh(scheme)
    return scheme


@router.get("/")
def list_schemes(
    db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    return db.query(Scheme).filter(Scheme.is_active == True).all()


@router.post("/enroll", status_code=201)
def enroll_customer(
    payload: SchemeEnroll,
    db: Session = Depends(get_shared_db),
    current_user=Depends(require_roles("owner", "manager")),
):
    scheme = db.query(Scheme).filter(Scheme.id == payload.scheme_id, Scheme.is_active == True).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    customer = db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    from dateutil.relativedelta import relativedelta
    end_date = payload.start_date + relativedelta(months=scheme.duration_months)

    # Generate account number
    count = db.query(SchemeAccount).count()
    account_number = f"SCH-{payload.start_date.strftime('%Y%m')}-{count + 1:05d}"

    account = SchemeAccount(
        account_number=account_number,
        scheme_id=scheme.id,
        customer_id=customer.id,
        start_date=payload.start_date,
        end_date=end_date,
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.post("/accounts/{account_id}/payment", status_code=201)
def record_payment(
    account_id: str,
    payload: SchemePayment,
    db: Session = Depends(get_shared_db),
    current_user=Depends(require_roles("owner", "manager", "salesman")),
):
    account = db.query(SchemeAccount).filter(SchemeAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Scheme account not found")

    if account.status != SchemeStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Account is not active")

    scheme = account.scheme
    if account.months_paid >= scheme.duration_months:
        raise HTTPException(status_code=400, detail="All installments already paid")

    txn = SchemeTransaction(
        account_id=account.id,
        payment_date=payload.payment_date,
        amount=payload.amount,
        gold_grams=payload.gold_grams,
        month_number=account.months_paid + 1,
        payment_mode=payload.payment_mode,
        receipt_number=payload.receipt_number,
        collected_by=current_user.id,
        notes=payload.notes,
    )
    account.months_paid += 1
    account.total_paid += payload.amount

    if account.months_paid >= scheme.duration_months:
        account.status = SchemeStatus.COMPLETED

    db.add(txn)
    db.commit()
    db.refresh(txn)
    return txn


@router.get("/accounts/{account_id}")
def get_account(
    account_id: str,
    db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    account = db.query(SchemeAccount).filter(SchemeAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account
