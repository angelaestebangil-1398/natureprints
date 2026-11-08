"""Perspective-correct print placement.

A room photo is described by one rectangle that really exists on the wall
(usually a frame already hanging there): its 4 corners in the photo (pixels)
and its real size in cm. From that we compute the wall's perspective
(a homography), so a new print of any size can be placed on the same wall
and gets the same angle and scale as the wall.

Wall coordinates are in cm: (0, 0) = top-left corner of the reference
rectangle, x to the right, y downwards.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageStat

import make_mockup as mm


def homography(src, dst):
    """3x3 matrix mapping src points (x, y) to dst points."""
    A = []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y, -u])
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y, -v])
    _, _, vt = np.linalg.svd(np.array(A, dtype=float))
    H = vt[-1].reshape(3, 3)
    return H / H[2, 2]


def apply(H, pts):
    out = []
    for x, y in pts:
        u, v, w = H @ np.array([x, y, 1.0])
        out.append((float(u / w), float(v / w)))
    return out


def wall_to_image(ref_quad, ref_w, ref_h):
    return homography([(0, 0), (ref_w, 0), (ref_w, ref_h), (0, ref_h)], ref_quad)


def build_art(photo_p, wcm, hcm, px_per_cm=12, frame_color=None, border_ratio=None):
    """The framed print as a flat image (frame + white paper border + photo)."""
    frame_color = frame_color or mm.FRAME_COLOR
    border_ratio = mm.BORDER if border_ratio is None else border_ratio
    W, H = round(wcm * px_per_cm), round(hcm * px_per_cm)
    frame = round(1.8 * px_per_cm)
    border = round(min(W, H) * border_ratio)
    paper = Image.new("RGB", (W - 2 * frame, H - 2 * frame), (247, 245, 240))
    inner = Image.open(photo_p).convert("RGB")
    iw, ih = paper.width - 2 * border, paper.height - 2 * border
    r = max(iw / inner.width, ih / inner.height)
    inner = inner.resize((round(inner.width * r), round(inner.height * r)), Image.LANCZOS)
    l, t = (inner.width - iw) // 2, (inner.height - ih) // 2
    paper.paste(inner.crop((l, t, l + iw, t + ih)), (border, border))
    art = Image.new("RGB", (W, H), frame_color)
    art.paste(paper, (frame, frame))
    if sum(frame_color) <= 450:
        d = ImageDraw.Draw(art)
        dark = tuple(int(c * 0.72) for c in frame_color)
        d.rectangle((0, 0, W - 1, H - 1), outline=dark, width=2)
        d.rectangle((frame - 1, frame - 1, W - frame, H - frame), outline=dark, width=2)
    if sum(frame_color) > 450:
        d = ImageDraw.Draw(art)
        d.rectangle((0, 0, W - 1, H - 1), outline=mm.FRAME_EDGE, width=2)
        d.rectangle((frame - 1, frame - 1, W - frame, H - frame), outline=mm.FRAME_EDGE, width=2)
    return art


def warp_onto(room, img, quad):
    """Warp img so its corners land on quad (TL, TR, BR, BL) in room. Returns (layer, mask)."""
    w, h = img.size
    H = homography(quad, [(0, 0), (w, 0), (w, h), (0, h)])  # room -> img (PIL wants inverse map)
    coeffs = (H.flatten() / H[2, 2])[:8]
    layer = img.transform(room.size, Image.PERSPECTIVE, tuple(coeffs), Image.BICUBIC)
    mask = Image.new("L", (w, h), 255).transform(room.size, Image.PERSPECTIVE, tuple(coeffs), Image.BICUBIC)
    return layer, mask


def keep_mask(original, box, rule):
    """Pixels in box that belong to objects in front of the wall (to restore over the print)."""
    m = Image.new("L", original.size, 0)
    px, mp = original.load(), m.load()
    x0, y0, x1, y1 = box
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = px[x, y]
            lum = 0.3 * r + 0.59 * g + 0.11 * b
            sat = (max(r, g, b) - min(r, g, b)) / max(1, max(r, g, b))
            if rule == "bluish":
                hit = b > r + 8
            elif rule == "green":
                hit = g > r + 10 and g > b
            elif rule == "dark":
                hit = lum < 80
            elif rule == "notwall":  # anything colourful or dark on a neutral wall
                hit = sat > 0.16 or lum < 120
            else:
                hit = False
            if hit:
                mp[x, y] = 255
    return m.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.8))


def mockup(room_p, original_p, photo_p, out_p, cfg, wcm, hcm):
    """cfg: ref (quad, w, h), cx and bottom in wall cm, crop, optional keep list."""
    room = Image.open(room_p).convert("RGB")
    original = Image.open(original_p).convert("RGB")
    Hw = wall_to_image(*cfg["ref"])
    cx, bottom = cfg["cx"], cfg["bottom"]
    corners_cm = [(cx - wcm / 2, bottom - hcm), (cx + wcm / 2, bottom - hcm), (cx + wcm / 2, bottom), (cx - wcm / 2, bottom)]
    quad = apply(Hw, corners_cm)

    # light level of the wall where the print hangs
    xs, ys = [p[0] for p in quad], [p[1] for p in quad]
    box = (int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys)))
    light = cfg.get("light") or max(0.82, min(1.0, ImageStat.Stat(room.crop(box).convert("L")).mean[0] / 215))

    art = build_art(photo_p, wcm, hcm).point(lambda v: int(v * light))
    layer, mask = warp_onto(room, art, quad)

    # soft shadow: same shape, shifted down a little (about 1 cm), blurred
    ppc = float(max(xs) - min(xs)) / wcm
    off = max(2, round(0.8 * ppc))
    shadow = mask.transform(room.size, Image.AFFINE, (1, 0, -off / 2, 0, 1, -off)).filter(ImageFilter.GaussianBlur(max(2, 1.3 * ppc)))
    shadow = shadow.point(lambda v: int(v * 0.42))
    room = Image.composite(Image.new("RGB", room.size, (20, 16, 12)), room, shadow)
    room = Image.composite(layer, room, mask)

    for kbox, rule in cfg.get("keep", []):
        room = Image.composite(original, room, keep_mask(original, kbox, rule))

    if cfg.get("crop"):
        x, y, w, h = cfg["crop"]
        room = room.crop((x, y, x + w, y + h))
    room.save(out_p, quality=90)
