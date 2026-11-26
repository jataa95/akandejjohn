"""Puts an unframed painting into the gallery frame used across the catalogue.

The frame, wall and floor come from the Young Virtuoso II photograph. To fit a
painting of different proportions, bands of plain moulding (the stretches between
the carved ornaments) are removed or repeated, so the ornaments themselves are
never stretched.

    python3 tools/frame_artwork.py <painting.jpg> <width> <height> <out.jpg>

<width> and <height> are the painting's real size in any unit (e.g. 36 48), used for
its proportions. White margins around the painting photo are trimmed first.
Needs Pillow and NumPy.
"""
import sys

import numpy as np
from PIL import Image, ImageChops, ImageFilter

TEMPLATE = "assets/img/works/originals/young-virtuoso-ii-frame-template.jpg"
OPEN = (172, 142, 776, 919)   # inner opening of the frame in the template: left, top, right, bottom
SCALE = 1.5                   # output is 1.5x the template for a sharper painting


def trim_white(im, thresh=22):
    bg = Image.new("RGB", im.size, (255, 255, 255))
    mask = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > thresh else 0)
    box = mask.getbbox()
    return im.crop(box) if box else im


def plain_bands(arr, axis, lo, hi, band_lo, band_hi, need):
    """Indices along `axis` (1 = columns, 0 = rows) inside [lo, hi) whose moulding is plain.

    Plainness is how little a column (or row) of the frame band differs from its neighbour;
    the `need` plainest positions are returned, spread over both halves of the edge.
    """
    a = arr.astype(np.int16)
    if axis == 1:
        band = np.concatenate([a[band_lo[0]:band_lo[1], :], a[band_hi[0]:band_hi[1], :]], 0)
        d = np.abs(np.diff(band, axis=1)).mean(axis=(0, 2))
    else:
        band = np.concatenate([a[:, band_lo[0]:band_lo[1]], a[:, band_hi[0]:band_hi[1]]], 1)
        d = np.abs(np.diff(band, axis=0)).mean(axis=(1, 2))
    d = np.convolve(d, np.ones(9) / 9, mode="same")   # prefer whole plain runs over single quiet lines
    mid = (lo + hi) // 2
    picks = []
    for a_, b_ in ((lo, mid), (mid, hi)):
        idx = np.arange(a_, b_)
        order = idx[np.argsort(d[a_:b_])]
        picks += sorted(order[: need // 2 + (need % 2 if a_ == lo else 0)])
    return sorted(picks)


def resize_axis(arr, axis, lo, hi, band_lo, band_hi, delta):
    """Remove (delta < 0) or repeat (delta > 0) plain lines along one axis."""
    if delta == 0:
        return arr
    picks = plain_bands(arr, axis, lo, hi, band_lo, band_hi, abs(delta))
    n = arr.shape[axis]
    keep = []
    pick = set(picks)
    for i in range(n):
        if delta < 0 and i in pick:
            continue
        keep.append(i)
        if delta > 0 and i in pick:
            keep.append(i)
    return np.take(arr, keep, axis=axis)


def frame(painting_path, pw, ph, out_path):
    tpl = Image.open(TEMPLATE).convert("RGB")
    L, T, R, B = OPEN
    ow, oh = R - L, B - T
    ratio = pw / ph
    # keep whichever opening side changes least, adjust the other to the painting's proportions
    if ratio >= ow / oh:
        tw, th = ow, round(ow / ratio)
    else:
        tw, th = round(oh * ratio), oh
    arr = np.asarray(tpl)
    # width: plain columns between the frame's corners, read from the top and bottom moulding
    arr = resize_axis(arr, 1, L + 20, R - 20, (T - 90, T - 10), (B + 10, B + 90), tw - ow)
    # height: plain rows between the corners, read from the left and right moulding
    L2, R2 = L, L + tw
    arr = resize_axis(arr, 0, T + 20, B - 20, (L2 - 90, L2 - 10), (R2 + 10, R2 + 90), th - oh)
    out = Image.fromarray(arr)
    out = out.resize((round(out.width * SCALE), round(out.height * SCALE)), Image.LANCZOS)

    # painting, cropped to the stated proportions and placed in the opening
    x0, y0 = round(L * SCALE), round(T * SCALE)
    w, h = round(tw * SCALE), round(th * SCALE)
    p = trim_white(Image.open(painting_path).convert("RGB"))
    pr = p.width / p.height
    if pr > w / h:
        nw = round(p.height * w / h)
        p = p.crop(((p.width - nw) // 2, 0, (p.width - nw) // 2 + nw, p.height))
    else:
        nh = round(p.width * h / w)
        p = p.crop((0, (p.height - nh) // 2, p.width, (p.height - nh) // 2 + nh))
    p = p.resize((w, h), Image.LANCZOS)
    # soft shadow cast by the frame's inner lip onto the canvas, and a touch of the gallery's warm light
    shade = Image.new("L", (w, h), 0)
    sm = np.zeros((h, w), np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    edge = np.minimum.reduce([xx, yy, w - 1 - xx, h - 1 - yy]).astype(np.float32)
    sm = np.clip(1 - edge / (0.035 * min(w, h)), 0, 1) ** 2 * 0.55
    sm += np.clip(1 - yy / (0.06 * h), 0, 1) * 0.15          # light from above: the top lip shades more
    shade = Image.fromarray((np.clip(sm, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2))
    p = Image.composite(Image.new("RGB", (w, h), (12, 9, 7)), p, shade)
    out.paste(p, (x0, y0))
    out.save(out_path, "JPEG", quality=88, optimize=True, progressive=True)
    return out.size


if __name__ == "__main__":
    src, pw, ph, dst = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    print(frame(src, pw, ph, dst))
