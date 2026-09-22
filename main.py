import copy
import random

import streamlit as st

from billing import Cart, new_invoice_no, make_txt, make_pdf, save_receipt
from products import PRODUCTS, flat_products, image_path

st.set_page_config(page_title="ShopEasy", page_icon="🛒", layout="wide")

if "cart" not in st.session_state:
    st.session_state.cart = Cart()
if "coupon" not in st.session_state:
    st.session_state.coupon = ""
st.session_state.setdefault("paid_order", None)
if "ratings" not in st.session_state:
    random.seed(7)
    st.session_state.ratings = {n: round(random.uniform(4.2, 4.9), 1) for n in flat_products()}
cart = st.session_state.cart

st.markdown("""
<style>
.stApp { background-color: #FAFAFA; }
.hero {
    background: linear-gradient(135deg, #0F3D3E, #146356);
    padding: 36px 40px; border-radius: 16px; color: white; margin-bottom: 24px;
}
.hero h1 { font-size: 2.2rem; margin: 6px 0; }
.badge {
    background: #FF4B6E; color: white; font-size: 11px; font-weight: 700;
    padding: 3px 10px; border-radius: 6px; display: inline-block; margin-bottom: 8px;
}
div[data-testid="stVerticalBlockBorderWrapper"] {
    height: 100%;
}
.prod-img {
    width: 100%; height: 160px; object-fit: cover;
    border-radius: 10px; margin-bottom: 10px;
}
.prod-cat { color: #888; font-size: 12px; letter-spacing: 1px; }
.prod-name { font-weight: 600; font-size: 15px; min-height: 40px; }
</style>
""", unsafe_allow_html=True)

st.markdown("## 🛒 ShopEasy")

st.markdown("""
<div class="hero">
  <div style="opacity:.8; letter-spacing:2px; font-size:12px;">FRESH FINDS · FAIR PRICES</div>
  <h1>Everything you need,<br>without the endless scroll.</h1>
  <p>Smart picks, honest prices, zero clutter. GST shown clearly at checkout — 18%.</p>
</div>
""", unsafe_allow_html=True)


@st.dialog("Choose payment", width="large")
def payment_window(items, bill, code):
    st.caption(f"Pay ₹{bill['total']}")
    method = st.radio(
        "Payment method",
        ["COD - Pay when your order arrives",
         "UPI - Google Pay, PhonePe or any UPI app",
         "Card - Credit or debit card"],
        label_visibility="collapsed",
    )
    upi_id = None
    if method.startswith("UPI"):
        upi_id = st.text_input("UPI ID", placeholder="yourname@upi")
    elif method.startswith("Card"):
        c1, c2 = st.columns(2)
        c1.text_input("Card number", placeholder="1234 5678 9012 3456")
        c2.text_input("Expiry", placeholder="MM/YY")

    if st.button(f"Pay ₹{bill['total']}", type="primary"):
        if method.startswith("UPI") and not upi_id:
            st.error("Enter a UPI ID to continue")
            return
        short_method = method.split(" - ")[0]
        inv = new_invoice_no()
        txt = make_txt(inv, items, bill, code, payment_method=short_method)
        pdf = make_pdf(inv, items, bill, code, payment_method=short_method)
        save_receipt(inv, txt, pdf)
        cart.items.clear()
        st.session_state.paid_order = {
            "inv": inv, "items": items, "bill": bill,
            "method": short_method, "txt": txt, "pdf": pdf,
        }
        st.rerun()


@st.dialog("🧾 Payment complete", width="large")
def receipt_window(order):
    st.success(f"Receipt {order['inv']}")
    st.caption(order["method"])
    for name, it in order["items"].items():
        st.write(f"{name} × {it['qty']}  —  ₹{it['price'] * it['qty']}")
    st.divider()
    bill = order["bill"]
    st.write(f"Subtotal: ₹{bill['subtotal']}")
    st.write(f"Discount: -₹{bill['discount']}")
    st.write(f"GST (18%): ₹{bill['gst']}")
    st.markdown(f"### Total paid: ₹{bill['total']}")

    d1, d2 = st.columns(2)
    d1.download_button("⬇️ TXT", order["txt"], file_name=f"{order['inv']}.txt", mime="text/plain")
    d2.download_button("⬇️ PDF", order["pdf"], file_name=f"{order['inv']}.pdf", mime="application/pdf")

    if st.button("Close"):
        st.session_state.paid_order = None
        st.rerun()


if st.session_state.get("paid_order"):
    receipt_window(st.session_state.paid_order)

left, right = st.columns([2, 1])

with left:
    st.subheader("Products")
    f1, f2 = st.columns([1, 2])
    category = f1.selectbox("Category", ["All"] + list(PRODUCTS.keys()))
    search = f2.text_input("Search", placeholder="Search products...")

    items = {
        n: v for n, v in flat_products().items()
        if (category == "All" or v[1] == category)
        and search.lower() in n.lower()
    }
    if not items:
        st.warning("No products found")

    cols = st.columns(3)
    for i, (name, (price, cat, emoji)) in enumerate(items.items()):
        with cols[i % 3]:
            with st.container(border=True, height=430):
                if i == 0 and category == "All" and not search:
                    st.markdown('<div class="badge">BESTSELLER</div>', unsafe_allow_html=True)

                img = image_path(name)
                if img:
                    st.markdown(
                        f'<img class="prod-img" src="data:image/jpeg;base64,'
                        f'{__import__("base64").b64encode(img.read_bytes()).decode()}">',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<div class="prod-img" style="display:flex;align-items:center;'
                        f'justify-content:center;font-size:52px;background:#F0F0F0;">{emoji}</div>',
                        unsafe_allow_html=True,
                    )

                st.markdown(f'<div class="prod-cat">{cat.upper()}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="prod-name">{name}</div>', unsafe_allow_html=True)
                r1, r2 = st.columns([1, 1])
                r1.write(f"₹{price}")
                r2.write(f"⭐ {st.session_state.ratings[name]}")
                qty = st.number_input("Qty", 1, 10, 1, key=f"q_{name}")
                if st.button("➕ Add to cart", key=f"b_{name}"):
                    cart.add(name, price, qty)
                    st.toast(f"Added {name}")

with right:
    st.subheader("Your cart")
    st.caption("Review quantities before checkout")
    if not cart.items:
        st.info("Cart is empty")
    for name, item in list(cart.items.items()):
        c1, c2 = st.columns([4, 1])
        c1.write(f"{name} × {item['qty']} = ₹{item['price'] * item['qty']}")
        if c2.button("🗑️", key=f"rm_{name}"):
            cart.remove(name)
            st.rerun()

    st.markdown("**Coupon code**")
    cc1, cc2 = st.columns([3, 1])
    coupon_input = cc1.text_input(
        "coupon", value=st.session_state.coupon,
        placeholder="SAVE10 or STUDENT20", label_visibility="collapsed",
    )
    if cc2.button("Apply"):
        st.session_state.coupon = coupon_input
        st.rerun()

    code = st.session_state.coupon
    bill = cart.bill(code)
    st.divider()
    st.write(f"Subtotal: ₹{bill['subtotal']}")
    st.write(f"GST (18%): ₹{bill['gst']}")
    if bill["discount"]:
        st.write(f"Discount: -₹{bill['discount']}")
    st.markdown(f"### Total: ₹{bill['total']}")

    if st.button("💳 Proceed to payment", type="primary", disabled=not cart.items):
        payment_window(copy.deepcopy(cart.items), bill, code)