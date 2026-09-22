import io
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer

GST_RATE = 0.18
DISCOUNT_CODES = {"SAVE10": 0.10, "STUDENT20": 0.20}
RECEIPTS_DIR = Path(__file__).parent / "receipts"


class Cart:
    def __init__(self):
        self.items = {}  # {name: {"price": float, "qty": int}}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("Quantity must be positive")
        if name in self.items:
            self.items[name]["qty"] += qty
        else:
            self.items[name] = {"price": price, "qty": qty}

    def remove(self, name):
        self.items.pop(name, None)

    def subtotal(self):
        return sum(i["price"] * i["qty"] for i in self.items.values())

    def bill(self, code=None):
        subtotal = self.subtotal()
        rate = DISCOUNT_CODES.get(code.strip().upper(), 0) if code else 0
        discount = subtotal * rate
        taxable = subtotal - discount
        gst = taxable * GST_RATE
        return {
            "subtotal": round(subtotal, 2),
            "discount": round(discount, 2),
            "gst": round(gst, 2),
            "total": round(taxable + gst, 2),
        }


# ---------- Receipts ----------

def new_invoice_no():
    return "INV-" + datetime.now().strftime("%Y%m%d-%H%M%S")


def _discount_label(bill, code):
    if code and bill["discount"]:
        return f"Discount ({code.strip().upper()})"
    return "Discount"


def make_txt(invoice_no, items, bill, code=None, payment_method=None):
    disc = -bill["discount"] if bill["discount"] else 0.0
    lines = [
        "=" * 44,
        "            SHOPEASY - TAX INVOICE",
        "=" * 44,
        f"Invoice : {invoice_no}",
        f"Date    : {datetime.now():%d-%m-%Y %H:%M}",
    ]
    if payment_method:
        lines.append(f"Payment : {payment_method}")
    lines += [
        "-" * 44,
        f"{'Item':<22}{'Qty':>4}{'Price':>8}{'Amt':>10}",
        "-" * 44,
    ]
    for name, it in items.items():
        amt = it["price"] * it["qty"]
        lines.append(f"{name[:21]:<22}{it['qty']:>4}{it['price']:>8}{amt:>10.2f}")
    lines += [
        "-" * 44,
        f"{'Subtotal':<34}{bill['subtotal']:>10.2f}",
        f"{_discount_label(bill, code):<34}{disc:>10.2f}",
        f"{'GST (18%)':<34}{bill['gst']:>10.2f}",
        "=" * 44,
        f"{'TOTAL':<34}{bill['total']:>10.2f}",
        "=" * 44,
        "      Thank you for shopping with us!",
    ]
    return "\n".join(lines)


def make_pdf(invoice_no, items, bill, code=None, payment_method=None):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("ShopEasy - Tax Invoice", styles["Title"]),
        Paragraph(f"Invoice: {invoice_no}", styles["Normal"]),
        Paragraph(f"Date: {datetime.now():%d-%m-%Y %H:%M}", styles["Normal"]),
    ]
    if payment_method:
        story.append(Paragraph(f"Payment: {payment_method}", styles["Normal"]))
    story.append(Spacer(1, 16))

    rows = [["Item", "Qty", "Price (Rs)", "Amount (Rs)"]]
    for name, it in items.items():
        rows.append([name, it["qty"], it["price"], f"{it['price'] * it['qty']:.2f}"])
    table = Table(rows, colWidths=[240, 50, 80, 90])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FF4B6E")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
    ]))
    story += [table, Spacer(1, 16)]

    disc = f"-{bill['discount']:.2f}" if bill["discount"] else "0.00"
    totals = [
        ["Subtotal", f"{bill['subtotal']:.2f}"],
        [_discount_label(bill, code), disc],
        ["GST (18%)", f"{bill['gst']:.2f}"],
        ["TOTAL", f"{bill['total']:.2f}"],
    ]
    tt = Table(totals, colWidths=[370, 90])
    tt.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 1, colors.black),
    ]))
    story += [tt, Spacer(1, 20),
              Paragraph("Thank you for shopping with us!", styles["Italic"])]

    doc.build(story)
    return buf.getvalue()


def save_receipt(invoice_no, txt, pdf_bytes):
    """Save a copy of the bill into the receipts/ folder."""
    RECEIPTS_DIR.mkdir(exist_ok=True)
    (RECEIPTS_DIR / f"{invoice_no}.txt").write_text(txt, encoding="utf-8")
    (RECEIPTS_DIR / f"{invoice_no}.pdf").write_bytes(pdf_bytes)
