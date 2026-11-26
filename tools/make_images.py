"""Makes the WebP sizes for every painting and the portrait, and records them in tools/imgs.json.

Run from the repository root after adding or replacing a JPEG in assets/img/works/:

    python3 tools/make_images.py

Needs Pillow (pip install Pillow).
"""
import glob
import json
import os

from PIL import Image

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
WIDTHS = [480, 800, 1200]

files = sorted(glob.glob(os.path.join(ROOT, "assets/img/works/*.jpg"))) + [os.path.join(ROOT, "assets/img/john-akande.jpg")]
manifest = {}
for path in files:
    im = Image.open(path).convert("RGB")
    w, h = im.size
    base = path[:-4]
    widths = [W for W in WIDTHS if W < w] + [w]
    for W in widths:
        out = f"{base}-{W}.webp"
        if not os.path.exists(out) or os.path.getmtime(out) < os.path.getmtime(path):
            (im if W == w else im.resize((W, round(h * W / w)), Image.LANCZOS)).save(out, "WEBP", quality=78, method=6)
    manifest[os.path.basename(base)] = {"w": w, "h": h, "ws": widths}

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "imgs.json"), "w") as f:
    json.dump(manifest, f, indent=0)
print(f"{len(manifest)} images ready")
