"""Remove existing art from a plain wall by filling a box with the wall colour
sampled just left and right of it (blended across, with a little grain)."""
from PIL import Image, ImageFilter
import random

def clear_box(im, box, margin=12, feather=0):
    """box must leave at least margin/4 px of plain wall around the art on every side."""
    x0, y0, x1, y1 = box
    original = im.copy()
    px = im.load()
    for y in range(y0, y1):
        l = [px[x0 - margin - i, y] for i in range(6)]
        r = [px[x1 + margin + i, y] for i in range(6)]
        L = [sum(c[k] for c in l) / 6 for k in range(3)]
        R = [sum(c[k] for c in r) / 6 for k in range(3)]
        for x in range(x0 - margin, x1 + margin):
            t = (x - (x0 - margin)) / (x1 - x0 + 2 * margin)
            n = random.uniform(-1.2, 1.2)
            px[x, y] = tuple(int(L[k] * (1 - t) + R[k] * t + n) for k in range(3))
    # soften the patch edges
    patch = im.crop((x0 - margin, y0 - 4, x1 + margin, y1 + 4)).filter(ImageFilter.GaussianBlur(1.2))
    im.paste(patch, (x0 - margin, y0 - 4))
    if feather:
        # smooth the filled area so no hard band shows, then blend its border softly
        from PIL import ImageDraw
        fill = im.crop((x0 - margin, y0, x1 + margin, y1)).filter(ImageFilter.GaussianBlur(feather))
        im.paste(fill, (x0 - margin, y0))
        mask = Image.new("L", im.size, 0)
        # blend only in the outer band of the patch (plain wall), never over the removed art
        b = max(4, margin // 4)
        ImageDraw.Draw(mask).rectangle((x0 - margin + b, y0 + b, x1 + margin - b, y1 - b), fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(b / 2))
        im.paste(Image.composite(im, original, mask))
    return im


def clear_profile(im, boxes, sample_x, feather=20):
    """Fill one or more boxes with the wall colour taken row by row from a clean
    vertical strip (sample_x = (x0, x1)), then blend the edges softly."""
    from PIL import ImageDraw
    original = im.copy()
    px = im.load()
    sx0, sx1 = sample_x
    mask = Image.new("L", im.size, 0)
    for (x0, y0, x1, y1) in boxes:
        for y in range(y0, y1):
            c = [sum(px[x, y][k] for x in range(sx0, sx1)) / (sx1 - sx0) for k in range(3)]
            for x in range(x0, x1):
                n = random.uniform(-1.0, 1.0)
                px[x, y] = tuple(int(c[k] + n) for k in range(3))
        ImageDraw.Draw(mask).rectangle((x0, y0, x1 - 1, y1 - 1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather / 3))
    return Image.composite(im, original, mask)


def clear_lr(im, boxes, feather=16):
    """boxes: list of (box, left_strip, right_strip). Each row is filled with a blend
    from the left strip colour to the right strip colour (left_strip=None: right only)."""
    from PIL import ImageDraw
    original = im.copy()
    px = im.load()
    mask = Image.new("L", im.size, 0)
    def avg(strip, y):
        a, b = strip
        return [sum(px[x, y][k] for x in range(a, b)) / (b - a) for k in range(3)]
    for entry in boxes:
        (x0, y0, x1, y1), left, right = entry[:3]
        polys = entry[3] if len(entry) > 3 else None
        for y in range(y0, y1):
            R = avg(right, y)
            L = avg(left, y) if left else R
            for x in range(x0, x1):
                t = (x - x0) / max(1, x1 - x0)
                n = random.uniform(-1.0, 1.0)
                px[x, y] = tuple(int(L[k] * (1 - t) + R[k] * t + n) for k in range(3))
        if polys:  # only repaint where the old frames were (plus a few px)
            for poly in polys:
                ImageDraw.Draw(mask).polygon(poly, fill=255)
        else:
            ImageDraw.Draw(mask).rectangle((x0, y0, x1 - 1, y1 - 1), fill=255)
    mask = mask.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(feather / 4))
    return Image.composite(im, original, mask)


def clear_tb(im, boxes, feather=16):
    """boxes: list of (box, top_rows, bottom_rows). Each column is filled with a blend
    from the wall colour just above the box to the colour just below it."""
    from PIL import ImageDraw
    original = im.copy()
    px = im.load()
    mask = Image.new("L", im.size, 0)
    def avg(x, rows):
        a, b = rows
        return [sum(px[x, y][k] for y in range(a, b)) / (b - a) for k in range(3)]
    for (x0, y0, x1, y1), top, bottom in boxes:
        for x in range(x0, x1):
            T, B = avg(x, top), avg(x, bottom)
            for y in range(y0, y1):
                t = (y - y0) / max(1, y1 - y0)
                n = random.uniform(-1.0, 1.0)
                px[x, y] = tuple(int(T[k] * (1 - t) + B[k] * t + n) for k in range(3))
        ImageDraw.Draw(mask).rectangle((x0, y0, x1 - 1, y1 - 1), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather / 3))
    return Image.composite(im, original, mask)


def clear_fit(im, polys, ring=30, pad=8, feather=10):
    """Repaint old frames (polygons) with a smooth wall: fit the wall's lighting
    (a gentle 2D curve) to a ring of wall pixels around the frames, then fill."""
    import numpy as np
    from PIL import ImageDraw
    frames = Image.new("L", im.size, 0)
    for poly in polys:
        ImageDraw.Draw(frames).polygon(poly, fill=255)
    inner = frames.filter(ImageFilter.MaxFilter(2 * pad + 1))
    outer = frames.filter(ImageFilter.MaxFilter(2 * (pad + ring) + 1))
    a = np.asarray(im).astype(float)
    ring_m = (np.asarray(outer) > 0) & ~(np.asarray(inner) > 0)
    ys, xs = np.nonzero(ring_m)
    sx, sy = im.width, im.height
    def feats(x, y):
        x, y = x / sx, y / sy
        return np.stack([np.ones_like(x), x, y, x * x, x * y, y * y, x ** 3, y ** 3], 1)
    F = feats(xs.astype(float), ys.astype(float))
    fy, fx = np.nonzero(np.asarray(inner) > 0)
    G = feats(fx.astype(float), fy.astype(float))
    out = a.copy()
    for c in range(3):
        coef, *_ = np.linalg.lstsq(F, a[ys, xs, c], rcond=None)
        out[fy, fx, c] = G @ coef + np.random.uniform(-1.0, 1.0, len(fx))
    filled = Image.fromarray(np.clip(out, 0, 255).astype("uint8"))
    mask = inner.filter(ImageFilter.GaussianBlur(feather / 3))
    return Image.composite(filled, im, mask)
