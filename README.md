# 🛒 ShopEasy

A Streamlit-based shopping and billing app. Browse products by category, search, add items to a cart, apply coupon codes, and check out with GST-inclusive invoicing — generating downloadable TXT and PDF receipts.

## Features

- **Product catalog** — organized by category (Electronics, Accessories, Stationery, Home & Study), with images, emoji fallbacks, and randomized star ratings
- **Search & filter** — filter by category and search by product name
- **Cart management** — add, remove, and update item quantities
- **Coupons** — `SAVE10` (10% off), `STUDENT20` (20% off)
- **GST calculation** — 18% tax applied automatically on the taxable amount
- **Checkout flow** — choose COD, UPI, or Card as payment method
- **Receipts** — auto-generated invoice number, downloadable as `.txt` and `.pdf` (via ReportLab), and saved locally under `receipts/`

## Project structure

```
ShoppingBillingSystem/
├── main.py               # Streamlit UI: product grid, cart, checkout, payment dialog
├── billing.py             # Cart logic, GST/discount calculation, TXT & PDF receipt generation
├── products.py             # Product catalog data and image path resolution
├── requirements.txt
├── .streamlit/
│   └── config.toml        # App theme
├── assets/                 # Product images (matched by slugified product name)
└── receipts/                # Generated receipts (git-ignored, except .gitkeep)
```

## Tech stack

- [Streamlit](https://streamlit.io/) — UI framework
- [ReportLab](https://www.reportlab.com/) — PDF generation
- Python 3.13

## Setup & running locally

1. Clone the repo:
   ```bash
   git clone <your-repo-url>
   cd ShoppingBillingSystem
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   streamlit run main.py
   ```

5. Open the app in your browser at `http://localhost:8501`.

## Configuration

The app theme is set in `.streamlit/config.toml`:

| Setting | Value |
|---|---|
| Base | Light |
| Primary color | `#FF4B6E` |
| Background | `#FFFFFF` |
| Secondary background | `#F5F5F7` |
| Text color | `#1A1A1A` |
| Font | Sans serif |

## Adding product images

Drop an image into `assets/` named after the product, slugified (lowercase, spaces/punctuation replaced with underscores), e.g. `Wireless Mouse` → `assets/wireless_mouse.jpg`. Supported extensions: `.png`, `.jpg`, `.jpeg`, `.webp`. Products without a matching image fall back to an emoji placeholder.

## Notes

- Generated receipts are stored in `receipts/` locally and are git-ignored (only `.gitkeep` is tracked) so real transaction data isn't committed to the repo.
- Coupon codes and GST rate are defined in `billing.py` and can be extended there.

## Roadmap

- [ ] Dockerize the app for consistent deployment
- [ ] Add CI (lint/test) via GitHub Actions
- [ ] Deploy to Streamlit Community Cloud / a cloud provider