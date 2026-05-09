from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.session import get_shared_db
from app.models.staff import Staff, StaffRole
from app.schemas.staff import StaffCreate, StaffResponse, StaffUpdate, LoginRequest, TokenResponse
from app.core.security import get_password_hash, verify_password, create_access_token, get_current_user, require_roles

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_shared_db)):
    staff = db.query(Staff).filter(Staff.phone == payload.phone, Staff.is_active == True).first()
    if not staff or not verify_password(payload.password, staff.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid phone number or password")

    token = create_access_token({"sub": str(staff.id), "role": staff.role.value})
    return TokenResponse(
        access_token=token,
        staff_id=str(staff.id),
        role=staff.role.value,
        name=staff.name,
    )


@router.post("/staff", response_model=StaffResponse, status_code=201)
def create_staff(
    payload: StaffCreate,
    db: Session = Depends(get_shared_db),
    _=Depends(require_roles("owner")),
):
    existing = db.query(Staff).filter(Staff.phone == payload.phone).first()
    if existing:
        raise HTTPException(status_code=409, detail="Phone number already registered")

    # Generate staff code
    count = db.query(Staff).filter(
        Staff.joined_date >= payload.joined_date.replace(day=1)
    ).count()

    staff = Staff(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        role=StaffRole(payload.role),
        joined_date=payload.joined_date,
        address=payload.address,
        hashed_password=get_password_hash(payload.password),
        staff_code=Staff.generate_staff_code(
            datetime.combine(payload.joined_date, datetime.min.time()),
            count + 1,
        ),
    )
    db.add(staff)
    db.commit()
    db.refresh(staff)
    return staff


@router.get("/staff/me", response_model=StaffResponse)
def get_me(current_user: Staff = Depends(get_current_user)):
    return current_user


@router.patch("/staff/{staff_id}", response_model=StaffResponse)
def update_staff(
    staff_id: str,
    payload: StaffUpdate,
    db: Session = Depends(get_shared_db),
    current_user: Staff = Depends(get_current_user),
):
    # Staff can update their own profile; owner can update anyone
    if str(current_user.id) != staff_id and current_user.role != StaffRole.OWNER:
        raise HTTPException(status_code=403, detail="Not authorized")

    staff = db.query(Staff).filter(Staff.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(staff, field, value)

    db.commit()
    db.refresh(staff)
    return staff
