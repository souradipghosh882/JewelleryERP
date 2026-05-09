from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.db.session import get_shared_db, get_pakka_db, get_kacha_db
from app.models.billing import PakkaSale, PakkaSaleItem, KachaSale, KachaSaleItem, BillStatus, PaymentMode
from app.models.ornament import Ornament, OrnamentStatus
from app.models.metal_rate import MetalRate
from app.models.customer import Customer
from app.models.staff import Staff
from app.schemas.billing import (
    PakkaSaleCreate, KachaSaleCreate,
    PakkaSaleResponse, KachaSaleResponse, CancelBillRequest,
)
from app.core.security import get_current_user, require_roles
from app.services.billing_service import (
    calculate_item_subtotal, calculate_pakka_total, calculate_old_gold_value, get_rate_for_metal
)
from app.services.pdf_service import generate_pakka_bill_pdf, generate_kacha_bill_pdf
from app.models.rokar import RokarEntry, RokarEntryType

router = APIRouter(prefix="/billing", tags=["Billing"])

SHOP_INFO = {
    "name": "Your Jewellery Shop",
    "address": "Shop Address, City - PIN",
    "gstin": "22AAAAA0000A1Z5",
}


def _get_latest_metal_rate(shared_db: Session) -> MetalRate:
    rate = shared_db.query(MetalRate).order_by(
        MetalRate.rate_date.desc(), MetalRate.created_at.desc()
    ).first()
    if not rate:
        raise HTTPException(status_code=503, detail="Metal rates not available. Please update rates first.")
    return rate


def _build_bill_number(prefix: str, db: Session, model) -> str:
    today = date.today().strftime("%Y%m%d")
    count = db.query(model).filter(
        model.bill_number.like(f"{prefix}-{today}-%")
    ).count()
    return f"{prefix}-{today}-{count + 1:04d}"


# ─── Pakka Bill ───────────────────────────────────────────────────────────────

@router.post("/pakka", response_model=PakkaSaleResponse, status_code=201)
def create_pakka_sale(
    payload: PakkaSaleCreate,
    pakka_db: Session = Depends(get_pakka_db),
    shared_db: Session = Depends(get_shared_db),
    current_user: Staff = Depends(require_roles("owner", "manager", "salesman")),
):
    # Validate customer
    customer = shared_db.query(Customer).filter(Customer.id == payload.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    metal_rate = _get_latest_metal_rate(shared_db)

    # Build items
    sale_items = []
    subtotal = 0.0
    for item_req in payload.items:
        ornament = shared_db.query(Ornament).filter(
            Ornament.id == item_req.ornament_id,
            Ornament.status == OrnamentStatus.IN_STOCK,
        ).first()
        if not ornament:
            raise HTTPException(status_code=400, detail=f"Ornament {item_req.ornament_id} not available")

        calcs = calculate_item_subtotal(ornament, metal_rate)

        # Apply making charge override if owner
        if item_req.making_charge_override is not None:
            if current_user.role.value != "owner":
                raise HTTPException(status_code=403, detail="Only owner can override making charges")
            calcs["making_charge_amount"] = round(item_req.making_charge_override, 2)
            calcs["item_subtotal"] = round(
                calcs["gold_value"] + calcs["making_charge_amount"] +
                calcs["stone_value"] + calcs["hallmark_charge"] + calcs["other_charges"], 2
            )

        subtotal += calcs["item_subtotal"]
        sale_items.append((ornament, calcs))

    # KYC check for amounts > 50k (Aadhaar), > 2L (PAN)
    totals = calculate_pakka_total(subtotal)
    if totals["total_amount"] > 200000 and not customer.pan_number:
        raise HTTPException(status_code=400, detail="PAN number required for transactions above ₹2 Lakh")
    if totals["total_amount"] > 50000 and not customer.aadhaar_number:
        raise HTTPException(status_code=400, detail="Aadhaar number required for transactions above ₹50,000")

    bill_number = _build_bill_number("PKK", pakka_db, PakkaSale)

    sale = PakkaSale(
        bill_number=bill_number,
        customer_id=customer.id,
        salesman_id=current_user.id,
        metal_rate_id=metal_rate.id,
        subtotal=round(subtotal, 2),
        gst_rate=totals["gst_rate"],
        gst_amount=totals["gst_amount"],
        total_amount=totals["total_amount"],
        payment_mode=payload.payment_mode,
        amount_paid=payload.amount_paid,
        balance_due=round(totals["total_amount"] - payload.amount_paid, 2),
        notes=payload.notes,
    )
    pakka_db.add(sale)
    pakka_db.flush()

    for ornament, calcs in sale_items:
        item = PakkaSaleItem(
            sale_id=sale.id,
            ornament_id=ornament.id,
            tag_code=ornament.tag_code,
            ornament_name=ornament.name,
            metal_type=ornament.metal_type.value,
            net_weight=ornament.net_weight,
            gold_rate=calcs["gold_rate"],
            gold_value=calcs["gold_value"],
            making_charge_type=ornament.making_charge_type,
            making_charge_value=ornament.making_charge_value,
            making_charge_amount=calcs["making_charge_amount"],
            stone_value=calcs["stone_value"],
            hallmark_charge=calcs["hallmark_charge"],
            other_charges=calcs["other_charges"],
            item_subtotal=calcs["item_subtotal"],
        )
        pakka_db.add(item)
        # Mark ornament as sold in shared DB
        ornament.status = OrnamentStatus.SOLD
        shared_db.add(ornament)

    shared_db.commit()
    pakka_db.commit()
    pakka_db.refresh(sale)
    return sale


@router.get("/pakka/{sale_id}", response_model=PakkaSaleResponse)
def get_pakka_sale(
    sale_id: str,
    pakka_db: Session = Depends(get_pakka_db),
    _=Depends(get_current_user),
):
    sale = pakka_db.query(PakkaSale).filter(PakkaSale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale


@router.get("/pakka/{sale_id}/pdf")
def download_pakka_pdf(
    sale_id: str,
    pakka_db: Session = Depends(get_pakka_db),
    shared_db: Session = Depends(get_shared_db),
    _=Depends(get_current_user),
):
    sale = pakka_db.query(PakkaSale).filter(PakkaSale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    customer = shared_db.query(Customer).filter(Customer.id == sale.customer_id).first()
    items = [
        {
            "tag_code": i.tag_code,
            "ornament_name": i.ornament_name,
            "net_weight": i.net_weight,
            "gold_rate": i.gold_rate,
            "gold_value": i.gold_value,
            "making_charge_amount": i.making_charge_amount,
            "stone_value": i.stone_value,
            "item_subtotal": i.item_subtotal,
        }
        for i in sale.items
    ]
    sale_dict = {
        "bill_number": sale.bill_number,
        "sale_date": sale.sale_date.strftime("%d/%m/%Y"),
        "subtotal": sale.subtotal,
        "gst_rate": sale.gst_rate,
        "gst_amount": sale.gst_amount,
        "total_amount": sale.total_amount,
        "payment_mode": sale.payment_mode.value,
    }
    pdf_bytes = generate_pakka_bill_pdf(sale_dict, {"name": customer.name, "phone": customer.phone}, items, SHOP_INFO)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={sale.bill_number}.pdf"},
    )


@router.post("/pakka/{sale_id}/cancel")
def cancel_pakka_sale(
    sale_id: str,
    payload: CancelBillRequest,
    pakka_db: Session = Depends(get_pakka_db),
    shared_db: Session = Depends(get_shared_db),
    current_user: Staff = Depends(require_roles("owner", "manager")),
):
    sale = pakka_db.query(PakkaSale).filter(PakkaSale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    if sale.status == BillStatus.CANCELLED:
        raise HTTPException(status_code=400, detail="Bill already cancelled")

    sale.status = BillStatus.CANCELLED
    sale.cancellation_reason = payload.reason

    # Restore ornaments to in_stock
    for item in sale.items:
        ornament = shared_db.query(Ornament).filter(Ornament.id == item.ornament_id).first()
        if ornament:
            ornament.status = OrnamentStatus.IN_STOCK
            shared_db.add(ornament)

    shared_db.commit()
    pakka_db.commit()
    return {"message": "Sale cancelled successfully"}


# ─── Kacha Bill ───────────────────────────────────────────────────────────────

@router.post("/kacha", response_model=KachaSaleResponse, status_code=201)
def create_kacha_sale(
    payload: KachaSaleCreate,
    kacha_db: Session = Depends(get_kacha_db),
    shared_db: Session = Depends(get_shared_db),
    current_user: Staff = Depends(require_roles("owner", "manager", "salesman")),
):
    metal_rate = _get_latest_metal_rate(shared_db)

    sale_items = []
    subtotal = 0.0
    for item_req in payload.items:
        ornament = shared_db.query(Ornament).filter(
            Ornament.id == item_req.ornament_id,
            Ornament.status == OrnamentStatus.IN_STOCK,
        ).first()
        if not ornament:
            raise HTTPException(status_code=400, detail=f"Ornament {item_req.ornament_id} not available")

        calcs = calculate_item_subtotal(ornament, metal_rate)
        subtotal += calcs["item_subtotal"]
        sale_items.append((ornament, calcs))

    # Old gold exchange (only in kacha)
    old_gold_value = 0.0
    if payload.old_gold_weight > 0 and payload.old_gold_purity:
        old_gold_value = calculate_old_gold_value(
            payload.old_gold_weight,
            payload.old_gold_purity,
            metal_rate.gold_24k,
        )

    total_amount = round(subtotal - old_gold_value, 2)
    bill_number = _build_bill_number("KCH", kacha_db, KachaSale)

    sale = KachaSale(
        bill_number=bill_number,
        customer_id=payload.customer_id,
        salesman_id=current_user.id,
        metal_rate_id=metal_rate.id,
        subtotal=round(subtotal, 2),
        old_gold_value=old_gold_value,
        old_gold_weight=payload.old_gold_weight,
        old_gold_purity=payload.old_gold_purity,
        total_amount=total_amount,
        payment_mode=payload.payment_mode,
        amount_paid=payload.amount_paid,
        balance_due=round(total_amount - payload.amount_paid, 2),
        notes=payload.notes,
    )
    kacha_db.add(sale)
    kacha_db.flush()

    for ornament, calcs in sale_items:
        item = KachaSaleItem(
            sale_id=sale.id,
            ornament_id=ornament.id,
            tag_code=ornament.tag_code,
            ornament_name=ornament.name,
            metal_type=ornament.metal_type.value,
            net_weight=ornament.net_weight,
            gold_rate=calcs["gold_rate"],
            gold_value=calcs["gold_value"],
            making_charge_type=ornament.making_charge_type,
            making_charge_value=ornament.making_charge_value,
            making_charge_amount=calcs["making_charge_amount"],
            stone_value=calcs["stone_value"],
            hallmark_charge=calcs["hallmark_charge"],
            other_charges=calcs["other_charges"],
            item_subtotal=calcs["item_subtotal"],
        )
        kacha_db.add(item)
        ornament.status = OrnamentStatus.SOLD
        shared_db.add(ornament)

    shared_db.commit()
    kacha_db.commit()
    kacha_db.refresh(sale)
    return sale


@router.get("/kacha/{sale_id}/pdf")
def download_kacha_pdf(
    sale_id: str,
    kacha_db: Session = Depends(get_kacha_db),
    shared_db: Session = Depends(get_shared_db),
    _=Depends(require_roles("owner", "manager", "salesman")),
):
    sale = kacha_db.query(KachaSale).filter(KachaSale.id == sale_id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")

    customer = None
    if sale.customer_id:
        customer = shared_db.query(Customer).filter(Customer.id == sale.customer_id).first()

    items = [
        {
            "tag_code": i.tag_code,
            "ornament_name": i.ornament_name,
            "net_weight": i.net_weight,
            "gold_rate": i.gold_rate,
            "gold_value": i.gold_value,
            "making_charge_amount": i.making_charge_amount,
            "stone_value": i.stone_value,
            "item_subtotal": i.item_subtotal,
        }
        for i in sale.items
    ]
    sale_dict = {
        "bill_number": sale.bill_number,
        "sale_date": sale.sale_date.strftime("%d/%m/%Y"),
        "subtotal": sale.subtotal,
        "old_gold_value": sale.old_gold_value,
        "old_gold_weight": sale.old_gold_weight,
        "old_gold_purity": sale.old_gold_purity,
        "total_amount": sale.total_amount,
    }
    customer_dict = {"name": customer.name, "phone": customer.phone} if customer else {}
    pdf_bytes = generate_kacha_bill_pdf(sale_dict, customer_dict, items, SHOP_INFO)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={sale.bill_number}.pdf"},
    )
