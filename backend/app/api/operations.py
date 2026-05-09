from datetime import date, datetime, time
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import qrcode, io, uuid

from app.db.session import get_shared_db
from app.models.staff import Staff, StaffAttendanceLog
from app.models.rokar import RokarEntry, RokarEntryType, BankLedgerEntry, Expense
from app.core.security import get_current_user, require_roles

router = APIRouter(prefix="/operations", tags=["Operations"])


# ─── Attendance ───────────────────────────────────────────────────────────────

class AttendanceScan(BaseModel):
    staff_id: str
    log_type: str  # "entry" or "exit"
    qr_code: str


def _determine_session(log_time: datetime) -> str:
    morning_start = time(9, 0)
    morning_end = time(14, 30)
    t = log_time.time()
    if morning_start <= t <= morning_end:
        return "morning"
    return "afternoon"


@router.post("/attendance/scan")
def record_attendance(
    payload: AttendanceScan,
    db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    staff = db.query(Staff).filter(Staff.id == payload.staff_id, Staff.is_active == True).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    if payload.log_type not in ("entry", "exit"):
        raise HTTPException(status_code=400, detail="log_type must be 'entry' or 'exit'")

    now = datetime.utcnow()
    log = StaffAttendanceLog(
        staff_id=staff.id,
        log_time=now,
        log_type=payload.log_type,
        session=_determine_session(now),
        qr_code=payload.qr_code,
    )
    db.add(log)
    db.commit()
    return {"message": f"Attendance {payload.log_type} recorded", "session": log.session}


@router.get("/attendance/today")
def today_attendance(
    db: Session = Depends(get_shared_db),
    _=Depends(require_roles("owner", "manager")),
):
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())
    logs = db.query(StaffAttendanceLog).filter(
        StaffAttendanceLog.log_time.between(today_start, today_end)
    ).all()
    return logs


# ─── Rokar (Cash Flow) ────────────────────────────────────────────────────────

class RokarEntryCreate(BaseModel):
    entry_date: date
    entry_type: RokarEntryType
    amount: float
    description: str
    reference_id: Optional[str] = None
    reference_type: Optional[str] = None


@router.post("/rokar", status_code=201)
def create_rokar_entry(
    payload: RokarEntryCreate,
    db: Session = Depends(get_shared_db),
    current_user=Depends(require_roles("owner", "manager", "accountant")),
):
    entry = RokarEntry(**payload.model_dump(), created_by=current_user.id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/rokar")
def get_rokar(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_shared_db),
    _=Depends(require_roles("owner", "manager", "accountant")),
):
    q = db.query(RokarEntry)
    if from_date:
        q = q.filter(RokarEntry.entry_date >= from_date)
    if to_date:
        q = q.filter(RokarEntry.entry_date <= to_date)
    entries = q.order_by(RokarEntry.entry_date.desc()).all()

    cash_in = sum(e.amount for e in entries if e.entry_type == RokarEntryType.CASH_IN)
    cash_out = sum(e.amount for e in entries if e.entry_type == RokarEntryType.CASH_OUT)
    return {
        "entries": entries,
        "total_cash_in": cash_in,
        "total_cash_out": cash_out,
        "net_cash": cash_in - cash_out,
    }


# ─── Bank Ledger ─────────────────────────────────────────────────────────────

class BankEntryCreate(BaseModel):
    bank_name: str
    account_number: str
    transaction_date: date
    transaction_type: str  # "credit" or "debit"
    amount: float
    description: str
    reference: Optional[str] = None
    balance_after: Optional[float] = None


@router.post("/bank-ledger", status_code=201)
def add_bank_entry(
    payload: BankEntryCreate,
    db: Session = Depends(get_shared_db),
    current_user=Depends(require_roles("owner", "accountant")),
):
    entry = BankLedgerEntry(**payload.model_dump(), created_by=current_user.id)
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("/bank-ledger")
def get_bank_ledger(
    account_number: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_shared_db),
    _=Depends(require_roles("owner", "accountant")),
):
    q = db.query(BankLedgerEntry)
    if account_number:
        q = q.filter(BankLedgerEntry.account_number == account_number)
    if from_date:
        q = q.filter(BankLedgerEntry.transaction_date >= from_date)
    if to_date:
        q = q.filter(BankLedgerEntry.transaction_date <= to_date)
    return q.order_by(BankLedgerEntry.transaction_date.desc()).all()


# ─── Expenses ─────────────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    expense_date: date
    category: str
    amount: float
    description: str
    payment_mode: str


@router.post("/expenses", status_code=201)
def add_expense(
    payload: ExpenseCreate,
    db: Session = Depends(get_shared_db),
    current_user=Depends(require_roles("owner", "manager")),
):
    from app.models.rokar import ExpenseCategory
    # Home expenses restricted to owner only
    if payload.category == "home" and current_user.role.value != "owner":
        raise HTTPException(status_code=403, detail="Only owner can record home expenses")

    expense = Expense(**payload.model_dump(), created_by=current_user.id)
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/expenses")
def list_expenses(
    category: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: Session = Depends(get_shared_db),
    current_user=Depends(require_roles("owner", "manager", "accountant")),
):
    q = db.query(Expense)
    # Manager cannot view home expenses
    if current_user.role.value == "manager":
        q = q.filter(Expense.category != "home")
    if category:
        q = q.filter(Expense.category == category)
    if from_date:
        q = q.filter(Expense.expense_date >= from_date)
    if to_date:
        q = q.filter(Expense.expense_date <= to_date)
    return q.order_by(Expense.expense_date.desc()).all()
