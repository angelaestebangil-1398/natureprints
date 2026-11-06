"""Build all room pictures for the shop.

    python3 tools/build_mockups.py

For every print it makes:
  images/rooms/<id>-print.jpg              the print alone on a light background
  images/rooms/<id>-<room>-<size>.jpg      the print hanging in a room, at real scale
and writes mockups.js, which the website reads.

Rooms live in rooms-src/. Each ROOM below says where the print hangs:
  ppc     pixels per cm on that wall (measured from the furniture)
  cx      horizontal centre of the print (centred above the furniture)
  bottom  bottom edge of the print (it grows upwards for bigger sizes)
  clear   areas of old art/objects to paint over with the wall colour
  crop    final 4:3 crop (x, y, w, h)
  max     biggest size that fits that wall
"""
import json
import os
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import make_mockup as mm  # noqa: E402
from clear_wall import clear_box, clear_lr, clear_profile, clear_tb  # noqa: E402

SIZES = {"40x50": (50, 40), "50x70": (70, 50), "70x100": (100, 70)}  # landscape w × h cm
ORDER = ["40x50", "50x70", "70x100"]

ROOMS = {
    "sideboard":     dict(label="Living room", ppc=4.55, cx=565, bottom=1150, crop=(0, 650, 1400, 1050),
                          clear=[("h", (265, 1035, 585, 1264), 20)]),
    "cabinet":       dict(label="Living room", ppc=5.4, cx=420, bottom=850, crop=(0, 380, 1400, 1050)),
    "console":       dict(label="Office", ppc=4.7, cx=780, bottom=360, crop=(100, 0, 1244, 933),
                          clear=[("h", (560, 215, 745, 418), 20)]),
    "white-living":  dict(label="Living room", ppc=6.3, cx=832, bottom=600, crop=(60, 0, 1547, 1160),
                          clear=[("hf", (240, 180, 1505, 620), 40)]),
    "grey-sofa":     dict(label="Living room", ppc=2.9, cx=368, bottom=415, crop=(0, 150, 687, 515),
                          clear=[("h", (245, 202, 560, 415), 10)]),
    "teal-living":   dict(label="Living room", light=1.0, ppc=3.4, cx=965, bottom=640, crop=(445, 150, 1040, 780),
                          clear=[("h", (650, 270, 1290, 638), 12)]),
    "dining":        dict(label="Kitchen", ppc=4.55, cx=495, bottom=700, crop=(0, 40, 1060, 795),
                          lr=[((283, 357, 715, 752), (262, 276), (728, 742))],
                          tb=[((514, 210, 720, 370), (196, 208), (382, 394))]),
    "kitchen-shelf": dict(label="Kitchen", ppc=5.2, cx=343, bottom=512, crop=(0, 150, 687, 515), max="40x50",
                          clear=[("h", (60, 222, 562, 512), 20)]),
    "bath-concrete": dict(label="Bathroom", ppc=6.0, cx=915, bottom=520, crop=(0, 60, 1400, 1050)),
    "bath-tiles":    dict(label="Bathroom", ppc=5.6, cx=300, bottom=345, crop=(0, 8, 1362, 1021), max="50x70"),
}

# Which rooms each print is shown in (first one = main picture)
PLAN = {
    "mallard-drake":    ["dining", "cabinet"],
    "mallard-hen":      ["kitchen-shelf", "sideboard"],
    "parakeet":         ["teal-living", "console"],
    "crested-tit":      ["grey-sofa", "cabinet"],
    "orb-spider":       ["console", "white-living"],
    "snipe":            ["white-living", "sideboard"],
    "mallard-profile":  ["bath-concrete", "bath-tiles"],
    "mallard-portrait": ["bath-tiles", "bath-concrete"],
    "ibex-mountain":    ["sideboard", "teal-living"],
    "ibex-portrait":    ["white-living", "cabinet"],
}

# Sizes each print is sold in (keep in line with products.js)
LIMITED = {"crested-tit": ["40x50", "50x70"], "ibex-mountain": ["40x50", "50x70"]}

OUT = os.path.join(ROOT, "images", "rooms")
WIDTH = 1400  # output width


def cleared_room(name):
    """Room photo with old art removed (cached in rooms-src/.cache)."""
    cache = os.path.join(ROOT, "rooms-src", ".cache", name + ".jpg")
    if os.path.exists(cache):
        return cache
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    cfg = ROOMS[name]
    im = Image.open(os.path.join(ROOT, "rooms-src", name + ".jpg")).convert("RGB")
    for mode, box, margin in cfg.get("clear", []):
        im = clear_box(im, box, margin=margin, feather=25 if mode == "hf" else 0)
    if "lr" in cfg:
        im = clear_lr(im, cfg["lr"])
    if "tb" in cfg:
        im = clear_tb(im, cfg["tb"])
    if "profile" in cfg:
        boxes, sample = cfg["profile"]
        im = clear_profile(im, boxes, sample)
    im.save(cache, quality=95)
    return cache


def finish(path):
    im = Image.open(path)
    if im.width > WIDTH:
        im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
    im.save(path, quality=82, optimize=True, progressive=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    data = {}
    for pid, rooms in PLAN.items():
        photo = os.path.join(ROOT, "images", pid + ".jpg")
        entry = {"print": f"images/rooms/{pid}-print.jpg", "rooms": []}
        mm.studio(photo, os.path.join(ROOT, entry["print"]))
        finish(os.path.join(ROOT, entry["print"]))
        for r in rooms:
            cfg = ROOMS[r]
            base = cleared_room(r)
            sizes = {}
            for size in LIMITED.get(pid, ORDER):
                if "max" in cfg and ORDER.index(size) > ORDER.index(cfg["max"]):
                    continue
                w, h = SIZES[size]
                rel = f"images/rooms/{pid}-{r}-{size}.jpg"
                mm.mockup(base, photo, os.path.join(ROOT, rel), cfg["ppc"], cfg["cx"], cfg["bottom"], w, h, cfg["crop"], cfg.get("light"))
                finish(os.path.join(ROOT, rel))
                sizes[size] = rel
            entry["rooms"].append({"id": r, "label": cfg["label"], "sizes": sizes})
        data[pid] = entry
        print("done", pid)
    with open(os.path.join(ROOT, "mockups.js"), "w") as f:
        f.write("/* Generated by tools/build_mockups.py. Do not edit by hand. */\n")
        f.write("const MOCKUPS = " + json.dumps(data, indent=2) + ";\n")


if __name__ == "__main__":
    main()
