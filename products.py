import re
from pathlib import Path

ASSETS_DIR = Path(__file__).parent / "assets"
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp")

PRODUCTS = {
    "Electronics": {
        "Wireless Mouse": (599, "🖱️"),
        "Mechanical Keyboard": (2499, "⌨️"),
        "USB-C Hub": (1299, "🔌"),
        "Headphones": (1999, "🎧"),
        "Webcam": (1499, "📷"),
        "Bluetooth Speaker": (1799, "🔊"),
        "Power Bank 20000mAh": (1599, "🔋"),
        "Smartwatch": (3499, "⌚"),
    },
    "Accessories": {
        "Laptop Stand": (899, "💻"),
        "Laptop Backpack": (1299, "🎒"),
        "Phone Stand": (349, "📱"),
        "Mouse Pad XL": (499, "🟦"),
        "Screen Cleaning Kit": (249, "🧽"),
        "Cable Organizer": (199, "🧵"),
    },
    "Stationery": {
        "Spiral Notebook (Pack of 3)": (249, "📓"),
        "Gel Pens (Pack of 10)": (150, "🖊️"),
        "Sticky Notes Set": (120, "🗒️"),
        "Desk Organizer": (449, "🗄️"),
        "Highlighters (Set of 6)": (180, "🖍️"),
    },
    "Home & Study": {
        "LED Desk Lamp": (799, "💡"),
        "Water Bottle 1L": (399, "🍶"),
        "Study Table Mat": (299, "🟫"),
        "Wall Clock": (549, "🕰️"),
        "Ergonomic Cushion": (699, "🛋️"),
    },
}


def flat_products():
    """Returns {name: (price, category, emoji)}."""
    return {
        name: (price, cat, emoji)
        for cat, items in PRODUCTS.items()
        for name, (price, emoji) in items.items()
    }


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def image_path(name):
    """Return the local image path if it exists, else None."""
    for ext in IMAGE_EXTS:
        p = ASSETS_DIR / f"{slugify(name)}{ext}"
        if p.exists():
            return p
    return None