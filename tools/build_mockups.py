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
from clear_wall import clear_box, clear_coons, clear_fit, clear_lr, clear_profile, clear_tb  # noqa: E402
import perspective  # noqa: E402

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
}

# Rooms placed with perspective: "ref" is a rectangle that really exists on the wall
# (the old frame): its 4 corners in the photo (TL, TR, BR, BL) and its real size in cm.
# cx / bottom are in wall cm, measured from that rectangle's top-left corner.
# only: sizes to render here (others show the nearest rendered size).
PROOMS = {
    "chair":     dict(label="Living room", ref=([(410, 137.5), (580, 137.5), (580, 367.5), (410, 367.5)], 50, 68),
                      cx=23.5, bottom=68, max="50x70", crop=(100, 160, 740, 555),
                      lr=[((403, 130, 588, 374), (392, 401), (392, 401))],
                      keep=[((586, 255, 640, 378), "notwall")]),
    "gold-sofa": dict(label="Living room", ref=([(352.5, 109), (463.5, 109), (463.5, 269), (352.5, 269)], 60, 86),
                      cx=69, bottom=86, crop=(125, 0, 675, 506),
                      fit=[[(351, 107), (465, 107), (465, 271), (351, 271)], [(492, 107), (607, 107), (607, 271), (492, 271)]]),
    "loft":      dict(label="Living room", ref=([(219, 556), (346, 596), (345, 776), (212.5, 762.5)], 40, 50),
                      cx=None, bottom=50, max="50x70", crop=(0, 430, 900, 675),
                      fit=[[(217, 553), (349, 594), (348, 779), (210, 765)], [(387, 602), (489, 632), (489, 795), (386, 785)]]),
    "dresser":   dict(label="Bedroom", ref=([(277, 15), (631, 15), (631, 255), (277, 255)], 100, 68),
                      cx=50, bottom=68, only=["70x100"], crop=(50, 0, 800, 600),
                      keep=[((238, 100, 300, 250), "bluish"), ((520, 235, 575, 275), "dark")]),
    # Tiled bathroom: the wall turns away from the camera. Its perspective comes from the
    # tile line (vanishing point about x=2212, y=560); the reference is a 100x70 cm area.
    "bath-tiles": dict(label="Bathroom", ref=([(120, -104.2), (557, 34.5), (557, 373.9), (120, 324.8)], 100, 70),
                      cx=35.7, bottom=70, max="50x70", crop=(0, 8, 1362, 1021),
                      keep=[((430, 170, 600, 430), "green")]),
    "nursery":   dict(label="Bedroom", ref=([(287.5, 367.5), (440, 367.5), (440, 552.5), (287.5, 552.5)], 45, 54),
                      cx=52.8, bottom=54, only=["70x100"], crop=(30, 230, 840, 630),
                      coons=[(280, 361, 449, 562), (487, 363, 654, 562)]),
    "dining-table": dict(label="Dining room", ref=([(305, 385), (672.5, 385), (672.5, 871), (305, 871)], 60, 80),
                      cx=30, bottom=80, crop=(0, 320, 900, 675),
                      coons=[(298, 379, 682, 880)],
                      keep=[((20, 715, 335, 940), "green")]),
    "bath-beige": dict(label="Bathroom", ref=([(551, 104), (659, 76.5), (660, 225), (552.5, 230)], 30, 40),
                      cx=None, bottom=40, max="40x50", crop=(290, 0, 610, 458),
                      coons=[(545, 70, 666, 238), (704, 15, 888, 229), (321, 142, 367, 250)]),
    "armchair-panel": dict(label="Living room", ref=([(383, 345), (631, 345), (631, 695), (383, 695)], 50, 70),
                      cx=25, bottom=70, max="50x70", crop=(110, 150, 790, 1020),
                      coons=[(376, 338, 638, 702)]),
    "desk":      dict(label="Office", ref=([(494, 143), (680, 143), (680, 392), (494, 392)], 30, 40),
                      cx=-6.6, bottom=37.3, max="50x70", crop=(60, 0, 840, 1123),
                      coons=[(486, 135, 688, 400)]),
    "beige-sofa": dict(label="Living room", ref=([(180, 108), (420, 108), (420, 290), (180, 290)], 60, 45),
                      cx=67.5, bottom=55.5, crop=(0, 0, 900, 600),
                      fit=[[(172, 100), (442, 100), (442, 308), (172, 308)], [(592, 26), (812, 26), (812, 270), (592, 270)]]),
    "plant-sofa": dict(label="Living room", ref=([(300, 100), (790, 100), (790, 590), (300, 590)], 100, 100),
                      cx=53, bottom=93.9, crop=(0, 0, 900, 1100)),
}
_Hb = perspective.wall_to_image(*PROOMS["bath-beige"]["ref"])
_rb = perspective.apply(__import__("numpy").linalg.inv(_Hb), [(881, 22), (881, 212.5)])
PROOMS["bath-beige"]["cx"] = round(sum(p[0] for p in _rb) / 2 / 2, 1)
# loft: centre the print between the left edge of the left frame and the right edge of the right frame
_H = perspective.wall_to_image(*PROOMS["loft"]["ref"])
_right_edge_cm = perspective.apply(__import__("numpy").linalg.inv(_H), [(486, 634), (486, 792.5)])
PROOMS["loft"]["cx"] = round((0 + sum(p[0] for p in _right_edge_cm) / 2) / 2, 1)

# Which rooms each print is shown in (first one = main picture)
PLAN = {
    "mallard-drake":    ["dining", "cabinet", "dresser", "beige-sofa"],
    "mallard-hen":      ["kitchen-shelf", "sideboard", "gold-sofa", "beige-sofa"],
    "parakeet":         ["teal-living", "chair", "plant-sofa"],
    "crested-tit":      ["grey-sofa", "cabinet", "loft", "desk"],
    "orb-spider":       ["gold-sofa", "white-living", "dresser", "desk"],
    "snipe":            ["white-living", "sideboard", "gold-sofa", "armchair-panel"],
    "mallard-profile":  ["bath-concrete", "bath-tiles", "chair", "bath-beige", "plant-sofa"],
    "mallard-portrait": ["bath-tiles", "bath-concrete", "loft", "bath-beige", "plant-sofa"],
    "ibex-mountain":    ["teal-living", "gold-sofa", "armchair-panel"],
    "ibex-portrait":    ["white-living", "cabinet", "dresser", "beige-sofa"],
    "blue-tit":         ["cabinet", "grey-sofa", "loft", "nursery", "armchair-panel"],
    "monk-parakeet":    ["teal-living", "dining", "chair", "beige-sofa"],
    "serins":           ["kitchen-shelf", "gold-sofa", "nursery", "desk"],
    "robin":            ["dining", "sideboard", "loft", "nursery", "armchair-panel"],
    "hoopoe":           ["white-living", "sideboard", "chair", "desk"],
}

# Sizes each print is sold in (keep in line with products.js)
LIMITED = {"crested-tit": ["40x50", "50x70"], "hoopoe": ["40x50", "50x70"]}

OUT = os.path.join(ROOT, "images", "rooms")
WIDTH = 1400  # output width


def cleared_room(name):
    """Room photo with old art removed (cached in rooms-src/.cache)."""
    cache = os.path.join(ROOT, "rooms-src", ".cache", name + ".jpg")
    if os.path.exists(cache):
        return cache
    os.makedirs(os.path.dirname(cache), exist_ok=True)
    cfg = ROOMS.get(name) or PROOMS[name]
    im = Image.open(os.path.join(ROOT, "rooms-src", name + ".jpg")).convert("RGB")
    for mode, box, margin in cfg.get("clear", []):
        im = clear_box(im, box, margin=margin, feather=25 if mode == "hf" else 0)
    if "lr" in cfg:
        im = clear_lr(im, cfg["lr"])
    if "coons" in cfg:
        im = clear_coons(im, cfg["coons"])
    if "fit" in cfg:
        im = clear_fit(im, cfg["fit"])
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


FRAMES = {"white": (243, 241, 237), "wood": (122, 84, 52)}  # frame colours shown on the website

# Sets: two prints that go together, hung side by side in one room.
# size: size of each print; gap: cm between them.
SETS = [
    dict(id="parakeets", title="The Parakeets", items=["parakeet", "monk-parakeet"], room="teal-living", size="50x70", gap=10),
    dict(id="pond", title="Life on the Pond", items=["mallard-drake", "mallard-hen"], room="sideboard", size="50x70", gap=10),
    dict(id="emerald", title="Emerald Mallards", items=["mallard-profile", "mallard-portrait"], room="gold-sofa", size="40x50", gap=10),
    dict(id="ibex", title="Alpine Ibex", items=["ibex-mountain", "ibex-portrait"], room="white-living", size="50x70", gap=12),
    dict(id="songbirds", title="Garden Songbirds", items=["blue-tit", "robin"], room="cabinet", size="40x50", gap=10),
    dict(id="pines", title="Birds of the Pines", items=["crested-tit", "serins"], room="loft", size="40x50", gap=10),
]


def render(room, pid, size, frame, out_rel, base=None, cx_shift=0, crop=True):
    """One print in one room. base: image to draw on (default: the cleared room).
    cx_shift: move the print sideways (cm). crop=False keeps the full room (for chaining)."""
    photo = os.path.join(ROOT, "images", pid + ".jpg")
    out = os.path.join(ROOT, out_rel)
    base = base or cleared_room(room)
    w, h = SIZES[size]
    mm.FRAME_COLOR = FRAMES[frame]
    if room in PROOMS:
        cfg = dict(PROOMS[room], cx=PROOMS[room]["cx"] + cx_shift)
        if not crop:
            cfg["crop"] = None
            cfg["keep"] = []
        perspective.mockup(base, os.path.join(ROOT, "rooms-src", room + ".jpg"), photo, out, cfg, w, h)
    else:
        cfg = ROOMS[room]
        mm.mockup(base, photo, out, cfg["ppc"], cfg["cx"] + cx_shift * cfg["ppc"], cfg["bottom"], w, h,
                  cfg["crop"] if crop else None, cfg.get("light"))
    if crop:
        finish(out)
    return out


def sizes_for(pid, room):
    cfg = ROOMS.get(room) or PROOMS[room]
    out = []
    for size in LIMITED.get(pid, ORDER):
        if "only" in cfg and size not in cfg["only"]:
            continue
        if "max" in cfg and ORDER.index(size) > ORDER.index(cfg["max"]):
            continue
        out.append(size)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    data = {}
    for pid, rooms in PLAN.items():
        photo = os.path.join(ROOT, "images", pid + ".jpg")
        entry = {"print": f"images/rooms/{pid}-print.jpg", "rooms": []}
        mm.studio(photo, os.path.join(ROOT, entry["print"]))
        finish(os.path.join(ROOT, entry["print"]))
        for r in rooms:
            cfg = ROOMS.get(r) or PROOMS[r]
            sizes = {}
            for size in sizes_for(pid, r):
                sizes[size] = {}
                for frame in FRAMES:
                    rel = f"images/rooms/{pid}-{r}-{size}-{frame}.jpg"
                    render(r, pid, size, frame, rel)
                    sizes[size][frame] = rel
            if sizes:
                entry["rooms"].append({"id": r, "label": cfg["label"], "sizes": sizes})
        data[pid] = entry
        print("done", pid)

    sets = []
    tmp = os.path.join(ROOT, "rooms-src", ".cache", "pair-tmp.jpg")
    for st in SETS:
        w = SIZES[st["size"]][0]
        shift = (w + st["gap"]) / 2
        images = {}
        for frame in FRAMES:
            rel = f"images/rooms/set-{st['id']}-{frame}.jpg"
            render(st["room"], st["items"][0], st["size"], frame, tmp, cx_shift=-shift, crop=False)
            render(st["room"], st["items"][1], st["size"], frame, rel, base=tmp, cx_shift=shift)
            images[frame] = rel
        sets.append(dict(id=st["id"], title=st["title"], items=st["items"], size=st["size"],
                         label=(ROOMS.get(st["room"]) or PROOMS[st["room"]])["label"], images=images))
        print("set", st["id"])

    with open(os.path.join(ROOT, "mockups.js"), "w") as f:
        f.write("/* Generated by tools/build_mockups.py. Do not edit by hand. */\n")
        f.write("const MOCKUPS = " + json.dumps(data, indent=2) + ";\n")
        f.write("const SETS = " + json.dumps(sets, indent=2) + ";\n")


if __name__ == "__main__":
    main()
