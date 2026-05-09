from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from pathlib import Path
import uuid, shutil

from app.db.session import get_shared_db
from app.models.ornament import Ornament, OrnamentStatus
from app.models.staff import Staff
from app.schemas.ornament import OrnamentCreate, OrnamentUpdate, OrnamentResponse
from app.core.security import get_current_user, require_roles
from app.services.tag_service import generate_tag_assets, compress_image
from app.core.config import settings

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.post("/ornaments", response_model=OrnamentResponse, status_code=201)
def create_ornament(
    payload: OrnamentCreate,
    db: Session = Depends(get_shared_db),
    current_user: Staff = Depends(require_roles("owner", "manager", "tagger")),
):
    # Compute next serial for tag code
    count = db.query(Ornament).filter(
        Ornament.category == payload.category,
        Ornament.metal_type == payload.metal_type,
    ).count()

    tag_code = Ornament.generate_tag_code(payload.metal_type, payload.category, count + 1)

    ornament = Ornament(
        tag_code=tag_code,
        created_by=current_user.id,
        **payload.model_dump(),
    )
    db.add(ornament)
    db.flush()

    # Generate QR + barcode
    assets = generate_tag_assets(tag_code, str(ornament.id))
    ornament.qr_path = assets["qr_path"]
    ornament.barcode_path = assets["barcode_path"]

    db.commit()
    db.refresh(ornament)
    return ornament


@router.post("/ornaments/{ornament_id}/photo")
def upload_ornament_photo(
    ornament_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_shared_db),
    current_user: Staff = Depends(require_roles("owner", "manager", "tagger")),
):
    ornament = db.query(Ornament).filter(Ornament.id == ornament_id).first()
    if not ornament:
        raise HTTPException(status_code=404, detail="Ornament not found")

    # Validate content type
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Only JPEG, PNG, and WebP images are allowed")

    upload_dir = Path(settings.UPLOAD_DIR) / "photos" / ornament_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    raw_path = str(upload_dir / f"raw_{file.filename}")

    with open(raw_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    compressed_path = str(upload_dir / "photo.jpg")
    compress_image(raw_path, compressed_path)
    Path(raw_path).unlink(missing_ok=True)

    ornament.photo_path = compressed_path
    db.commit()
    return {"photo_path": compressed_path}


@router.get("/ornaments", response_model=List[OrnamentResponse])
def list_ornaments(
    status: Optional[str] = None,
    metal_type: Optional[str] = None,
    category: Optional[str] = None,
    search: Optional[str] = Query(None, description="Search by name or tag code"),
    limit: int = Query(50, le=200),
    offset: int = 0,
    db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    q = db.query(Ornament)
    if status:
        q = q.filter(Ornament.status == status)
    if metal_type:
        q = q.filter(Ornament.metal_type == metal_type)
    if category:
        q = q.filter(Ornament.category == category)
    if search:
        q = q.filter(
            (Ornament.name.ilike(f"%{search}%")) | (Ornament.tag_code.ilike(f"%{search}%"))
        )
    return q.offset(offset).limit(limit).all()


@router.get("/ornaments/{ornament_id}", response_model=OrnamentResponse)
def get_ornament(
    ornament_id: str,
    db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    ornament = db.query(Ornament).filter(Ornament.id == ornament_id).first()
    if not ornament:
        raise HTTPException(status_code=404, detail="Ornament not found")
    return ornament


@router.get("/scan/{tag_code}", response_model=OrnamentResponse)
def scan_ornament(
    tag_code: str,
    db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    ornament = db.query(Ornament).filter(Ornament.tag_code == tag_code).first()
    if not ornament:
        raise HTTPException(status_code=404, detail=f"No ornament found for tag: {tag_code}")
    return ornament


@router.patch("/ornaments/{ornament_id}", response_model=OrnamentResponse)
def update_ornament(
    ornament_id: str,
    payload: OrnamentUpdate,
    db: Session = Depends(get_shared_db),
    current_user: Staff = Depends(require_roles("owner", "manager", "tagger")),
):
    ornament = db.query(Ornament).filter(Ornament.id == ornament_id).first()
    if not ornament:
        raise HTTPException(status_code=404, detail="Ornament not found")

    if ornament.status == OrnamentStatus.SOLD:
        raise HTTPException(status_code=400, detail="Cannot edit a sold ornament")

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(ornament, field, value)

    db.commit()
    db.refresh(ornament)
    return ornament
