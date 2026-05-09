from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.db.session import get_shared_db, get_pakka_db, get_kacha_db
from app.models.metal_rate import MetalRate, MetalRateSession
from app.models.billing import PakkaSale, KachaSale, BillStatus
from app.models.ornament import Ornament, OrnamentStatus
from app.schemas.metal_rate import MetalRateCreate, MetalRateResponse, CurrentRates
from app.core.security import require_roles, get_current_user

router = APIRouter(prefix="/rates", tags=["Metal Rates"])


@router.post("/", response_model=MetalRateResponse, status_code=201)
def set_metal_rate(
    payload: MetalRateCreate,
    shared_db: Session = Depends(get_shared_db),
    current_user=Depends(require_roles("owner")),
):
    # Upsert: if same date+session exists, update it
    existing = shared_db.query(MetalRate).filter(
        MetalRate.rate_date == payload.rate_date,
        MetalRate.session == payload.session,
    ).first()

    if existing:
        for field, value in payload.model_dump().items():
            setattr(existing, field, value)
        existing.updated_by = current_user.id
        shared_db.commit()
        shared_db.refresh(existing)
        return existing

    rate = MetalRate(**payload.model_dump(), updated_by=current_user.id)
    shared_db.add(rate)
    shared_db.commit()
    shared_db.refresh(rate)
    return rate


@router.get("/current", response_model=CurrentRates)
def get_current_rates(
    shared_db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    rate = shared_db.query(MetalRate).order_by(
        MetalRate.rate_date.desc(), MetalRate.created_at.desc()
    ).first()
    if not rate:
        raise HTTPException(status_code=404, detail="No metal rates found")

    is_stale = rate.rate_date < date.today()
    return CurrentRates(
        rate_date=rate.rate_date,
        session=rate.session,
        gold_22k=rate.gold_22k,
        gold_18k=rate.gold_18k,
        gold_24k=rate.gold_24k,
        gold_14k=rate.gold_14k,
        gold_9k=rate.gold_9k,
        silver=rate.silver,
        silver_925=rate.silver_925,
        is_stale=is_stale,
    )


@router.get("/history", response_model=List[MetalRateResponse])
def get_rate_history(
    days: int = Query(30, le=365),
    shared_db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    from datetime import timedelta
    since = date.today() - timedelta(days=days)
    rates = shared_db.query(MetalRate).filter(
        MetalRate.rate_date >= since
    ).order_by(MetalRate.rate_date.desc(), MetalRate.session.desc()).all()
    return rates


# ─── Analytics ────────────────────────────────────────────────────────────────

analytics_router = APIRouter(prefix="/analytics", tags=["Analytics"])


@analytics_router.get("/dashboard")
def get_dashboard(
    period: str = Query("today", description="today | week | month | year"),
    pakka_db: Session = Depends(get_pakka_db),
    kacha_db: Session = Depends(get_kacha_db),
    shared_db: Session = Depends(get_shared_db),
    current_user=Depends(require_roles("owner", "manager", "accountant")),
):
    today = date.today()

    if period == "today":
        start = datetime.combine(today, datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
    elif period == "week":
        from datetime import timedelta
        start = datetime.combine(today - timedelta(days=7), datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
    elif period == "month":
        start = datetime.combine(today.replace(day=1), datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
    elif period == "year":
        start = datetime.combine(today.replace(month=1, day=1), datetime.min.time())
        end = datetime.combine(today, datetime.max.time())
    else:
        raise HTTPException(status_code=400, detail="Invalid period")

    # Pakka sales summary
    pakka_result = pakka_db.query(
        func.count(PakkaSale.id).label("count"),
        func.coalesce(func.sum(PakkaSale.total_amount), 0).label("total"),
        func.coalesce(func.sum(PakkaSale.gst_amount), 0).label("gst_collected"),
    ).filter(
        PakkaSale.sale_date.between(start, end),
        PakkaSale.status == BillStatus.ACTIVE,
    ).first()

    # Kacha sales summary
    kacha_result = kacha_db.query(
        func.count(KachaSale.id).label("count"),
        func.coalesce(func.sum(KachaSale.total_amount), 0).label("total"),
    ).filter(
        KachaSale.sale_date.between(start, end),
        KachaSale.status == BillStatus.ACTIVE,
    ).first()

    # Inventory summary
    inventory_summary = shared_db.query(
        Ornament.status,
        func.count(Ornament.id).label("count"),
    ).group_by(Ornament.status).all()

    # Metal stock weight
    gold_stock = shared_db.query(
        func.coalesce(func.sum(Ornament.net_weight), 0)
    ).filter(
        Ornament.status == OrnamentStatus.IN_STOCK,
        Ornament.metal_type.in_(["gold_22k", "gold_18k", "gold_24k", "gold_14k", "gold_9k"]),
    ).scalar()

    return {
        "period": period,
        "pakka": {
            "sales_count": pakka_result.count,
            "total_amount": float(pakka_result.total),
            "gst_collected": float(pakka_result.gst_collected),
        },
        "kacha": {
            "sales_count": kacha_result.count,
            "total_amount": float(kacha_result.total),
        },
        "combined_revenue": float(pakka_result.total) + float(kacha_result.total),
        "inventory": {s.status: s.count for s in inventory_summary},
        "gold_stock_grams": float(gold_stock or 0),
    }


@analytics_router.get("/sales/trend")
def sales_trend(
    months: int = Query(6, le=24),
    pakka_db: Session = Depends(get_pakka_db),
    kacha_db: Session = Depends(get_kacha_db),
    _=Depends(require_roles("owner", "manager", "accountant")),
):
    """Monthly sales trend for charts."""
    pakka_monthly = pakka_db.query(
        extract("year", PakkaSale.sale_date).label("year"),
        extract("month", PakkaSale.sale_date).label("month"),
        func.sum(PakkaSale.total_amount).label("total"),
        func.count(PakkaSale.id).label("count"),
    ).filter(PakkaSale.status == BillStatus.ACTIVE).group_by("year", "month").order_by("year", "month").all()

    kacha_monthly = kacha_db.query(
        extract("year", KachaSale.sale_date).label("year"),
        extract("month", KachaSale.sale_date).label("month"),
        func.sum(KachaSale.total_amount).label("total"),
        func.count(KachaSale.id).label("count"),
    ).filter(KachaSale.status == BillStatus.ACTIVE).group_by("year", "month").order_by("year", "month").all()

    return {
        "pakka": [{"year": r.year, "month": r.month, "total": float(r.total), "count": r.count} for r in pakka_monthly],
        "kacha": [{"year": r.year, "month": r.month, "total": float(r.total), "count": r.count} for r in kacha_monthly],
    }
