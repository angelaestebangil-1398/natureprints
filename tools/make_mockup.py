"""Place a print on a room photo at real scale.
usage: python3 make_mockup.py room.jpg photo.jpg out.jpg px_per_cm center_x bottom_y print_w_cm print_h_cm [crop_x crop_y crop_w crop_h]
"""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageStat

# Look of the print on the wall
FRAME_COLOR = (243, 241, 237)   # white frame
FRAME_EDGE = (205, 200, 192)    # thin darker edge so a white frame shows on white walls
BORDER = 0.06                   # white paper border around the photo (0 = photo to the edge)

def mockup(room_p, photo_p, out_p, ppc, cx, bottom, wcm, hcm, crop=None, light=None,
           frame_color=None, border_ratio=None):
    frame_color = frame_color or FRAME_COLOR
    border_ratio = BORDER if border_ratio is None else border_ratio
    room = Image.open(room_p).convert("RGB")
    W, H = round(wcm * ppc), round(hcm * ppc)
    frame = max(2, round(1.8 * ppc))      # 1.8 cm thin frame
    border = round(min(W, H) * border_ratio)  # white paper border
    x0, y0 = round(cx - W / 2), round(bottom - H)

    # light level of the wall where the print hangs -> darken print to match
    wall = room.crop((x0, y0, x0 + W, y0 + H)).convert("L")
    if light is None:
        light = max(0.8, min(1.0, ImageStat.Stat(wall).mean[0] / 215))

    paper = Image.new("RGB", (W - 2 * frame, H - 2 * frame), (247, 245, 240))
    inner = Image.open(photo_p).convert("RGB")
    iw, ih = paper.width - 2 * border, paper.height - 2 * border
    r = max(iw / inner.width, ih / inner.height)
    inner = inner.resize((round(inner.width * r), round(inner.height * r)), Image.LANCZOS)
    inner = inner.crop(((inner.width - iw) // 2, (inner.height - ih) // 2, (inner.width - iw) // 2 + iw, (inner.height - ih) // 2 + ih))
    paper.paste(inner, (border, border))
    art = Image.new("RGB", (W, H), frame_color)
    art.paste(paper, (frame, frame))
    if sum(frame_color) <= 450:  # wood frame: darker edges give it depth
        d = ImageDraw.Draw(art)
        dark = tuple(int(c * 0.72) for c in frame_color)
        d.rectangle((0, 0, W - 1, H - 1), outline=dark)
        d.rectangle((frame - 1, frame - 1, W - frame, H - frame), outline=dark)
    if sum(frame_color) > 450:  # light frame: outline it so it reads against the wall
        d = ImageDraw.Draw(art)
        d.rectangle((0, 0, W - 1, H - 1), outline=FRAME_EDGE)
        d.rectangle((frame - 1, frame - 1, W - frame, H - frame), outline=FRAME_EDGE)
    art = art.point(lambda v: int(v * light))

    # soft shadow below/right
    sh = Image.new("L", room.size, 0)
    off = max(3, round(0.9 * ppc))
    sh.paste(110, (x0 + off // 2, y0 + off, x0 + W + off // 2, y0 + H + off))
    sh = sh.filter(ImageFilter.GaussianBlur(max(3, round(1.4 * ppc))))
    room = Image.composite(Image.new("RGB", room.size, (20, 16, 12)), room, sh)
    room.paste(art, (x0, y0))
    if crop:
        x, y, w, h = crop
        room = room.crop((x, y, x + w, y + h))
    room.save(out_p, quality=88)

if __name__ == "__main__":
    a = sys.argv
    crop = tuple(map(int, a[9:13])) if len(a) > 9 else None
    mockup(a[1], a[2], a[3], float(a[4]), float(a[5]), float(a[6]), float(a[7]), float(a[8]), crop)

def studio(photo_p, out_p, size=(1400, 1050), bg=(236, 235, 232)):
    """Print only (no frame), big and straight on, on a light background."""
    from PIL import ImageDraw
    canvas = Image.new("RGB", size, bg)
    photo = Image.open(photo_p).convert("RGB")
    W = int(size[0] * 0.74)
    border = int(W * 0.045)
    iw = W - 2 * border
    ih = int(iw * photo.height / photo.width)
    photo = photo.resize((iw, ih), Image.LANCZOS)
    H = ih + 2 * border
    x0, y0 = (size[0] - W) // 2, (size[1] - H) // 2
    sh = Image.new("L", size, 0)
    ImageDraw.Draw(sh).rectangle((x0 + 6, y0 + 14, x0 + W + 6, y0 + H + 14), fill=90)
    sh = sh.filter(ImageFilter.GaussianBlur(18))
    canvas = Image.composite(Image.new("RGB", size, (60, 55, 50)), canvas, sh)
    paper = Image.new("RGB", (W, H), (250, 249, 246))
    paper.paste(photo, (border, border))
    canvas.paste(paper, (x0, y0))
    canvas.save(out_p, quality=88)
