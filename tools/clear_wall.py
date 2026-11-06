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
