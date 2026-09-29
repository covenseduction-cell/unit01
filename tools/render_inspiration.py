#!/usr/bin/env python3
"""Draws the credits page's real-world locator map as SVG: the British Isles on the
British National Grid, with the Caeldun world's footprint boxed, plus a close-up.

Usage: python3 tools/render_inspiration.py <ne_10m_admin_0_countries.geojson>
Writes ../maps/inspiration-uk.svg and ../maps/inspiration-zoom.svg.
Coastlines: Natural Earth (public domain).
"""
import json
import math
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "maps"

# World frame on the National Grid (1 block = 4 m): E 107500 +- 65536, N 800000 +- 90112.
BOX = (107500 - 65536, 800000 - 90112, 107500 + 65536, 800000 + 90112)


def osgb(lon, lat):
    """WGS84 lon/lat -> OSGB36 easting/northing (Airy 1830 transverse Mercator; datum shift ignored, ~100 m)."""
    a, b = 6377563.396, 6356256.909
    F0, lat0, lon0, N0, E0 = 0.9996012717, math.radians(49), math.radians(-2), -100000, 400000
    e2 = 1 - (b * b) / (a * a)
    n = (a - b) / (a + b)
    phi, lam = math.radians(lat), math.radians(lon)
    s, c = math.sin(phi), math.cos(phi)
    nu = a * F0 / math.sqrt(1 - e2 * s * s)
    rho = a * F0 * (1 - e2) / (1 - e2 * s * s) ** 1.5
    eta2 = nu / rho - 1
    dp, sp = phi - lat0, phi + lat0
    M = b * F0 * ((1 + n + 1.25 * n * n + 1.25 * n ** 3) * dp
                  - (3 * n + 3 * n * n + 2.625 * n ** 3) * math.sin(dp) * math.cos(sp)
                  + (1.875 * n * n + 1.875 * n ** 3) * math.sin(2 * dp) * math.cos(2 * sp)
                  - (35 / 24) * n ** 3 * math.sin(3 * dp) * math.cos(3 * sp))
    t = math.tan(phi)
    I = M + N0
    II = nu / 2 * s * c
    III = nu / 24 * s * c ** 3 * (5 - t * t + 9 * eta2)
    IIIA = nu / 720 * s * c ** 5 * (61 - 58 * t * t + t ** 4)
    IV = nu * c
    V = nu / 6 * c ** 3 * (nu / rho - t * t)
    VI = nu / 120 * c ** 5 * (5 - 18 * t * t + t ** 4 + 14 * eta2 - 58 * t * t * eta2)
    dl = lam - lon0
    N = I + II * dl ** 2 + III * dl ** 4 + IIIA * dl ** 6
    E = E0 + IV * dl + V * dl ** 3 + VI * dl ** 5
    return E, N


def rings(geom):
    polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in polys:
        for ring in poly:
            yield ring


def svg_map(features, view, width, path, box=True, labels=(), stroke=0.9, title="", fill=True):
    e0, n0, e1, n1 = view
    height = width * (n1 - n0) / (e1 - e0)
    sx = width / (e1 - e0)

    def pt(e, n):
        return (e - e0) * sx, (n1 - n) * sx

    parts = []
    for f in features:
        for ring in rings(f["geometry"]):
            pts = [osgb(lon, lat) for lon, lat in ring]
            es = [p[0] for p in pts]; ns = [p[1] for p in pts]
            if max(es) < e0 or min(es) > e1 or max(ns) < n0 or min(ns) > n1:
                continue
            d = "M" + " L".join("%.1f %.1f" % pt(e, n) for e, n in pts) + "Z"
            parts.append(d)
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" role="img" aria-label="{title}">',
           f'<rect width="{width:.0f}" height="{height:.0f}" fill="#dbe9f1"/>',
           f'<path d="{" ".join(parts)}" fill="#ecebe4" stroke="#7d8a93" stroke-width="{stroke}" stroke-linejoin="round"/>']
    if box:
        x0, y0 = pt(BOX[0], BOX[3]); x1, y1 = pt(BOX[2], BOX[1])
        out.append(f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" fill="{"rgba(200,50,40,.12)" if fill else "none"}" stroke="#c8322a" stroke-width="2.2"/>')
    for text, e, n, size, style in labels:
        x, y = pt(e, n)
        out.append(f'<text x="{x:.1f}" y="{y:.1f}" font-family="-apple-system,Segoe UI,Arial,sans-serif" font-size="{size}" '
                   f'text-anchor="middle" fill="{"#c8322a" if style == "box" else "#54595d"}" font-weight="{700 if style == "box" else 400}" '
                   f'{"font-style=" + chr(34) + "italic" + chr(34) if style == "sea" else ""} paint-order="stroke" stroke="#fff" stroke-width="3">{text}</text>')
    out.append("</svg>")
    path.write_text("\n".join(out))
    print("wrote", path, len(parts), "rings")


def main():
    data = json.loads(Path(sys.argv[1]).read_text())
    keep = {"GBR", "IRL", "IMN", "FRA", "GGY", "JEY"}
    feats = [f for f in data["features"] if f["properties"].get("ADM0_A3") in keep]
    OUT.mkdir(exist_ok=True)
    svg_map(feats, (-120000, 0, 680000, 1220000), 520, OUT / "inspiration-uk.svg", stroke=0.8,
            title="Map of Great Britain and Ireland with the area the world is based on outlined",
            labels=[("Scotland", 280000, 760000, 16, ""), ("England", 430000, 330000, 16, ""),
                    ("Wales", 290000, 250000, 13, ""), ("Ireland", 10000, 260000, 16, ""),
                    ("Atlantic Ocean", -40000, 900000, 14, "sea"), ("North Sea", 560000, 700000, 14, "sea"),
                    ("Caeldun Isles", BOX[0] + 65000, BOX[3] + 22000, 14, "box")])
    pad = 12000
    svg_map(feats, (BOX[0] - pad, BOX[1] - pad, BOX[2] + pad, BOX[3] + pad), 520, OUT / "inspiration-zoom.svg", stroke=0.7, fill=False,
            title="Close-up of the real coastline inside the outlined area",
            labels=[("Outer Hebrides", 78000, 870000, 13, ""), ("Skye", 145000, 845000, 14, ""),
                    ("Rùm", 137000, 791000, 12, ""), ("Canna", 124000, 809500, 11, ""), ("Coll", 126000, 764500, 12, ""),
                    ("Tiree", 96000, 736000, 12, ""), ("Mull", 158000, 722000, 13, ""),
                    ("Ardnamurchan", 170000, 773000, 12, ""), ("Barra", 55000, 800000, 12, "")])


if __name__ == "__main__":
    main()
