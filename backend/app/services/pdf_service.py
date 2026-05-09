import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors


def generate_pakka_bill_pdf(sale: dict, customer: dict, items: list, shop_info: dict) -> bytes:
    """Generate a legal Pakka bill PDF with GST details."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # Header
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 20 * mm, shop_info.get("name", "Jewellery Shop"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 27 * mm, shop_info.get("address", ""))
    c.drawCentredString(width / 2, height - 32 * mm, f"GSTIN: {shop_info.get('gstin', '')}")

    # Bill info
    c.setFont("Helvetica-Bold", 12)
    c.drawString(15 * mm, height - 45 * mm, "TAX INVOICE (PAKKA BILL)")
    c.setFont("Helvetica", 10)
    c.drawString(15 * mm, height - 52 * mm, f"Bill No: {sale['bill_number']}")
    c.drawString(15 * mm, height - 57 * mm, f"Date: {sale['sale_date']}")
    c.drawString(100 * mm, height - 52 * mm, f"Customer: {customer['name']}")
    c.drawString(100 * mm, height - 57 * mm, f"Phone: {customer['phone']}")

    # Items table
    table_data = [["Tag Code", "Item", "Wt(g)", "Rate", "Gold Val", "Making", "Stone", "Total"]]
    for item in items:
        table_data.append([
            item["tag_code"],
            item["ornament_name"][:20],
            f"{item['net_weight']:.3f}",
            f"₹{item['gold_rate']:.0f}",
            f"₹{item['gold_value']:.2f}",
            f"₹{item['making_charge_amount']:.2f}",
            f"₹{item['stone_value']:.2f}",
            f"₹{item['item_subtotal']:.2f}",
        ])

    table = Table(table_data, colWidths=[22*mm, 40*mm, 15*mm, 18*mm, 22*mm, 20*mm, 18*mm, 22*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
    ]))
    table.wrapOn(c, width - 30 * mm, height)
    table.drawOn(c, 15 * mm, height - 120 * mm)

    # Totals
    y = height - 135 * mm
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 15 * mm, y, f"Subtotal: ₹{sale['subtotal']:.2f}")
    y -= 6 * mm
    c.drawRightString(width - 15 * mm, y, f"GST ({sale['gst_rate'] * 100:.0f}%): ₹{sale['gst_amount']:.2f}")
    y -= 6 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 15 * mm, y, f"TOTAL: ₹{sale['total_amount']:.2f}")
    y -= 10 * mm
    c.setFont("Helvetica", 9)
    c.drawString(15 * mm, y, f"Payment Mode: {sale['payment_mode'].upper()}")
    c.drawString(15 * mm, y - 6 * mm, "Thank you for your purchase!")

    c.save()
    buffer.seek(0)
    return buffer.read()


def generate_kacha_bill_pdf(sale: dict, customer: dict, items: list, shop_info: dict) -> bytes:
    """Generate internal Kacha bill PDF (no GST, may include old gold exchange)."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, height - 20 * mm, shop_info.get("name", "Jewellery Shop"))
    c.setFont("Helvetica", 10)
    c.drawCentredString(width / 2, height - 27 * mm, shop_info.get("address", ""))

    c.setFont("Helvetica-Bold", 12)
    c.drawString(15 * mm, height - 42 * mm, "BILL (INTERNAL)")
    c.setFont("Helvetica", 10)
    c.drawString(15 * mm, height - 49 * mm, f"Bill No: {sale['bill_number']}")
    c.drawString(15 * mm, height - 54 * mm, f"Date: {sale['sale_date']}")
    if customer:
        c.drawString(100 * mm, height - 49 * mm, f"Customer: {customer['name']}")

    table_data = [["Tag Code", "Item", "Wt(g)", "Rate", "Gold Val", "Making", "Stone", "Total"]]
    for item in items:
        table_data.append([
            item["tag_code"],
            item["ornament_name"][:20],
            f"{item['net_weight']:.3f}",
            f"₹{item['gold_rate']:.0f}",
            f"₹{item['gold_value']:.2f}",
            f"₹{item['making_charge_amount']:.2f}",
            f"₹{item['stone_value']:.2f}",
            f"₹{item['item_subtotal']:.2f}",
        ])

    table = Table(table_data, colWidths=[22*mm, 40*mm, 15*mm, 18*mm, 22*mm, 20*mm, 18*mm, 22*mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
    ]))
    table.wrapOn(c, width - 30 * mm, height)
    table.drawOn(c, 15 * mm, height - 115 * mm)

    y = height - 130 * mm
    c.setFont("Helvetica", 10)
    c.drawRightString(width - 15 * mm, y, f"Subtotal: ₹{sale['subtotal']:.2f}")

    if sale.get("old_gold_weight", 0) > 0:
        y -= 6 * mm
        c.drawRightString(
            width - 15 * mm, y,
            f"Old Gold Exchange ({sale['old_gold_weight']}g {sale.get('old_gold_purity', '')}): "
            f"-₹{sale['old_gold_value']:.2f}"
        )

    y -= 6 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawRightString(width - 15 * mm, y, f"TOTAL: ₹{sale['total_amount']:.2f}")
    y -= 10 * mm
    c.setFont("Helvetica", 9)
    c.drawString(15 * mm, y, "Payment Mode: CASH")
    c.drawString(15 * mm, y - 6 * mm, "Thank you for your purchase!")

    c.save()
    buffer.seek(0)
    return buffer.read()
