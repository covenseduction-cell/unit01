#!/usr/bin/env python3
"""Renders the wiki's world maps from the Caeldun world builder's global arrays.

Reads SkyeWorld/data/world/g/*.npy (50 m survey grid, north up) and the Find
overlays fetched from the Skye studio, and writes into ../maps/:

  world.jpg        physical map (relief, lochs, coast, region borders)
  base.jpg         muted base for the thematic maps
  layers/<id>.png  one transparent overlay per ore / tree / crop, cropped to the world
  maps.json        region label points and layer metadata

Usage: python3 tools/render_maps.py <overlay-dir> [find.json]
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "maps"
G = Path.home() / "Desktop/MCServer/SkyeWorld/data/world/g"
ATLAS = Path.home() / "Desktop/MCServer/plugins/Skye/atlas.json"

# Survey grid: E 38000..178000, N 704000..896000 at 50 m. World frame (1 block = 4 m):
# E 107500 +- 65536, N 800000 +- 90112.
E0, N1, POST = 38000, 896000, 50.0
C0, C1 = round((107500 - 65536 - E0) / POST), round((107500 + 65536 - E0) / POST)
R0, R1 = round((N1 - (800000 + 90112)) / POST), round((N1 - (800000 - 90112)) / POST)

LAND_COLOURS = {"outer": "#c8b489", "north": "#7fb0a0", "spider": "#a58fc4", "bread": "#e0bd52", "rain": "#6fbf63"}
REGION_LAND = {1: "outer", 2: "outer", 3: "north", 4: "north", 5: "north", 6: "spider", 7: "spider", 8: "spider",
               9: "bread", 10: "bread", 11: "rain", 12: "rain", 13: "rain", 14: "north"}


RENAME = {"Scots pine": "Pine"}


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def ramp(values, stops):
    xs = np.array([s[0] for s in stops], np.float32)
    cols = np.stack([hexrgb(s[1]) for s in stops])
    out = np.empty(values.shape + (3,), np.float32)
    for c in range(3):
        out[..., c] = np.interp(values, xs, cols[:, c])
    return out


def hillshade(z, az=315, alt=45, exaggerate=2.2):
    gy, gx = np.gradient(z * exaggerate, POST)
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy))
    aspect = np.arctan2(-gx, gy)
    a, al = np.radians(az), np.radians(alt)
    s = np.sin(al) * np.sin(slope) + np.cos(al) * np.cos(slope) * np.cos(a - aspect)
    return np.clip(s, 0, 1)


def edges(mask):
    m = mask
    e = np.zeros_like(m)
    e[1:, :] |= m[1:, :] != m[:-1, :]
    e[:, 1:] |= m[:, 1:] != m[:, :-1]
    return e


def main():
    overlays = Path(sys.argv[1])
    find = json.loads(Path(sys.argv[2]).read_text()) if len(sys.argv) > 2 else None
    OUT.mkdir(exist_ok=True)
    (OUT / "layers").mkdir(exist_ok=True)

    crop = (slice(R0, R1), slice(C0, C1))
    raw = np.load(G / "raw.npy", mmap_mode="r")[crop].astype(np.float32)
    ocean = np.load(G / "ocean.npy", mmap_mode="r")[crop]
    loch = np.load(G / "loch_id.npy", mmap_mode="r")[crop] > 0
    dland = np.load(G / "dland.npy", mmap_mode="r")[crop]
    region = np.load(G / "region.npy", mmap_mode="r")[crop]
    heat = np.load(G / "heat.npy", mmap_mode="r")[crop]
    land = ~ocean & ~loch
    H, W = raw.shape
    print("grid", W, H)

    relief = np.where(land, np.maximum(raw, 0), 0)
    shade = hillshade(relief)
    shade = 0.55 + 0.45 * (shade / max(shade[land].mean(), 1e-6)).clip(0, 1.6) / 1.6 * 1.0

    # --- physical map ---
    landcol = ramp(relief, [(0, "#b5d3a6"), (40, "#a3c792"), (150, "#b3c98f"), (300, "#cdd09a"),
                            (500, "#ddd2a8"), (700, "#d9c7ae"), (850, "#eee8e0"), (1000, "#ffffff")])
    seacol = ramp(dland, [(0, "#cbe7f5"), (350, "#b9dcef"), (900, "#9ec9e6"), (2500, "#86b6da"), (8000, "#77a8d0")])
    img = np.where(land[..., None], landcol * shade[..., None], seacol)
    img = np.where(loch[..., None], hexrgb("#c4e3f3"), img)
    hot = np.clip((heat - 0.05) / 0.6, 0, 1) * land
    img = img * (1 - hot[..., None] * 0.55) + hexrgb("#5a2a22") * (hot[..., None] * 0.55)

    coast = edges(land) & ~(loch & ~ocean)
    img[edges(ocean)] = hexrgb("#4f7fa3")
    img[edges(loch) & land] = hexrgb("#6f9fc0")
    border = np.zeros_like(land)
    rg = np.where(land, region, 0)
    border[1:, :] |= (rg[1:, :] != rg[:-1, :]) & (rg[1:, :] > 0) & (rg[:-1, :] > 0)
    border[:, 1:] |= (rg[:, 1:] != rg[:, :-1]) & (rg[:, 1:] > 0) & (rg[:, :-1] > 0)
    thick = border.copy()
    thick[1:, :] |= border[:-1, :]
    thick[:, 1:] |= border[:, :-1]
    border = thick & land
    img[border] = img[border] * 0.3 + hexrgb("#7a6a8a") * 0.7
    Image.fromarray(img.clip(0, 255).astype(np.uint8)).save(OUT / "world.jpg", quality=86, optimize=True, progressive=True)

    # --- muted base for thematic maps ---
    grey = ramp(relief, [(0, "#eeede8"), (400, "#e2e0d8"), (900, "#f7f6f2")]) * (0.72 + 0.28 * shade[..., None] / shade.max())
    base = np.where(land[..., None], grey, hexrgb("#dbe9f1"))
    base = np.where(loch[..., None], hexrgb("#dbe9f1"), base)
    base[edges(ocean)] = hexrgb("#8aa6ba")
    base[border] = base[border] * 0.5 + hexrgb("#9a94a6") * 0.5
    Image.fromarray(base.clip(0, 255).astype(np.uint8)).save(OUT / "base.jpg", quality=86, optimize=True, progressive=True)

    # --- region label points: the land cell nearest each region's land centroid ---
    atlas = json.loads(ATLAS.read_text())
    names = {r["id"]: r["name"] for r in atlas["regions"]}
    labels = []
    ys, xs = np.nonzero(land)
    rs = region[ys, xs]
    for rid in range(1, 15):
        sel = rs == rid
        if not sel.any():
            continue
        cy, cx = ys[sel].mean(), xs[sel].mean()
        k = np.argmin((ys[sel] - cy) ** 2 + (xs[sel] - cx) ** 2)
        labels.append({"id": rid, "name": names[rid], "land": REGION_LAND[rid],
                       "x": float(xs[sel][k] / W), "y": float(ys[sel][k] / H)})
    hy, hx = np.nonzero((heat > 0.6) & land)
    if len(hy):
        labels.append({"id": 15, "name": "The Burning Isle", "land": "hell",
                       "x": float(hx.mean() / W), "y": float(hy.mean() / H)})

    # --- overlays: Find PNGs are square over the world's long side; keep the world's columns ---
    layers = []
    groups = find["groups"] if find else []
    for g in groups:
        for it in g["items"]:
            src = overlays / f'{it["id"]}.png'
            if not src.exists():
                print("missing", it["id"])
                continue
            im = Image.open(src).convert("RGBA")
            side = im.width
            lo = round(side * (22528 - 16384) / 45056)
            im = im.crop((lo, 0, side - lo, side))
            # The studio draws traces as dots and planned regions as hatching; soften both into washes.
            im = im.filter(ImageFilter.GaussianBlur(1.4))
            im.quantize(64, method=Image.Quantize.FASTOCTREE).save(OUT / "layers" / f'{it["id"]}.png', optimize=True)
            layers.append({"id": it["id"], "group": g["id"], "name": RENAME.get(it["name"], it["name"]), "colour": it["colour"],
                           "share": it.get("share"), "peak": it.get("peak")})

    meta = {"width": W, "height": H, "blocks": [32768, 45056], "labels": labels,
            "lands": LAND_COLOURS, "groups": [{"id": g["id"], "label": g["label"], "about": g.get("about", "")} for g in groups],
            "layers": layers}
    (OUT / "maps.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    print("labels", len(labels), "layers", len(layers))


if __name__ == "__main__":
    main()
