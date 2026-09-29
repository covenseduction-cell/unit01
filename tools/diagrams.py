#!/usr/bin/env python3
"""Block-grid diagrams for the wiki (side views), written as SVG into ../assets/diagrams/.

Each diagram is a grid of characters, one per block, top row first:
  .  air          ~  water         G  grass on dirt    D  dirt        R  natural rock
  S  stone        C  cobblestone   B  stone bricks     L  log         P  planks
  F  wooden fence K  chain         W  wool             T  lantern     s  scaffolding
  x  (any block marked to fall: drawn with a red outline and a cross)
Lower-case letters b/l/p/c/w are the same block marked as falling.
Run: python3 tools/diagrams.py
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "diagrams"
CELL = 22

FILL = {
    "G": ("#6f9a4a", "#8a6a45"), "D": ("#8a6a45", None), "R": ("#8d8d88", None), "S": ("#a4a49f", None),
    "C": ("#8f8f8a", None), "B": ("#9c9c96", None), "L": ("#7a5a36", None), "P": ("#c19a5e", None),
    "F": ("#b08850", None), "K": ("#5c6166", None), "W": ("#f2f0ea", None), "T": ("#3a3a3a", None),
    "s": ("#d9c27a", None), "~": ("#9cc6e0", None), "o": ("#b08850", None),
}
FALLING = {"b": "B", "l": "L", "p": "P", "c": "C", "w": "W", "x": "S", "r": "S"}


def block(ch, x, y):
    s = []
    fall = ch in FALLING
    base = FALLING.get(ch, ch)
    if base == ".":
        return ""
    col, second = FILL[base]
    c = CELL
    if base == "F":      # fence: a post
        s.append(f'<rect x="{x + c*.36:.1f}" y="{y}" width="{c*.28:.1f}" height="{c}" fill="{col}" stroke="#6b4f2a"/>')
        s.append(f'<rect x="{x}" y="{y + c*.25:.1f}" width="{c}" height="{c*.14:.1f}" fill="{col}" opacity=".6"/>')
    elif base == "K":    # chain
        for i in range(3):
            s.append(f'<ellipse cx="{x + c/2}" cy="{y + c*(i+.5)/3:.1f}" rx="{c*.13:.1f}" ry="{c*.17:.1f}" fill="none" stroke="{col}" stroke-width="2"/>')
    elif base == "T":    # lantern
        s.append(f'<rect x="{x + c*.28:.1f}" y="{y + c*.25:.1f}" width="{c*.44:.1f}" height="{c*.6:.1f}" rx="2" fill="#f4c24a" stroke="{col}" stroke-width="2"/>')
    elif base == "s":    # scaffolding
        s.append(f'<rect x="{x+1}" y="{y+1}" width="{c-2}" height="{c-2}" fill="none" stroke="#b89a40" stroke-width="2.5"/>')
        s.append(f'<path d="M{x+2} {y+c-2}L{x+c-2} {y+2}" stroke="#b89a40" stroke-width="2"/>')
    elif base == "o":    # a post seen from above
        s.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" fill="#f7fbfd"/>')
        s.append(f'<circle cx="{x + c/2}" cy="{y + c/2}" r="{c*.3:.1f}" fill="#b08850" stroke="#6b4f2a" stroke-width="1.5"/>')
    elif base == "~":
        s.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" fill="{col}"/>')
    else:
        s.append(f'<rect x="{x}" y="{y}" width="{c}" height="{c}" fill="{col}" stroke="rgba(0,0,0,.25)"/>')
        if base == "G":
            s.append(f'<rect x="{x}" y="{y + c*.28:.1f}" width="{c}" height="{c*.72:.1f}" fill="{second}"/>')
        if base == "L":
            s.append(f'<path d="M{x + c*.3:.1f} {y}V{y+c}M{x + c*.68:.1f} {y}V{y+c}" stroke="#5e4428" stroke-width="1.3"/>')
        if base == "P":
            s.append(f'<path d="M{x} {y + c/2}H{x+c}M{x + c*.5:.1f} {y}V{y + c/2}M{x + c*.2:.1f} {y + c/2}V{y+c}" stroke="#9c7a44" stroke-width="1"/>')
        if base == "B":
            s.append(f'<path d="M{x} {y + c/2}H{x+c}M{x + c/2} {y}V{y + c/2}M{x + c*.25:.1f} {y + c/2}V{y+c}M{x + c*.75:.1f} {y + c/2}V{y+c}" stroke="#7c7c76" stroke-width="1"/>')
        if base == "W":
            s.append(f'<path d="M{x+4} {y+7}h{c-8}M{x+4} {y+c-7}h{c-8}" stroke="#d8d4c8" stroke-width="1.2"/>')
    if fall:
        s.append(f'<rect x="{x+1.5}" y="{y+1.5}" width="{c-3}" height="{c-3}" fill="rgba(210,50,40,.18)" stroke="#d2322a" stroke-width="2.4"/>')
        s.append(f'<path d="M{x+6} {y+6}L{x+c-6} {y+c-6}M{x+c-6} {y+6}L{x+6} {y+c-6}" stroke="#d2322a" stroke-width="2.2"/>')
    return "".join(s)


def diagram(name, rows, notes=(), title="", marks=(), bands=()):
    """notes: (col, row, text, anchor) placed at cell coordinates; marks: extra SVG in cell units."""
    w = max(len(r) for r in rows)
    h = len(rows)
    pad_top = 8
    W, H = w * CELL + 16, h * CELL + 16 + pad_top
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-label="{title}" font-family="-apple-system,Segoe UI,Arial,sans-serif">',
           f'<rect width="{W}" height="{H}" fill="#f7fbfd"/>', f'<g transform="translate(8 {8 + pad_top})">']
    for (r0, r1, colour, label) in bands:   # horizontal zones, in rows
        out.append(f'<rect x="0" y="{r0*CELL}" width="{w*CELL}" height="{(r1-r0)*CELL}" fill="{colour}"/>')
        if label:
            out.append(f'<text x="{w*CELL - 4}" y="{r0*CELL + 13}" text-anchor="end" font-size="11" font-weight="700" fill="#54595d">{label}</text>')
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            out.append(block(ch, i * CELL, j * CELL))
    for m in marks:
        out.append(m(CELL))
    for (col, row, text, anchor) in notes:
        out.append(f'<text x="{col*CELL:.1f}" y="{row*CELL:.1f}" text-anchor="{anchor}" font-size="12" fill="#202122" '
                   f'paint-order="stroke" stroke="#f7fbfd" stroke-width="4" stroke-linejoin="round">{text}</text>')
    out.append("</g></svg>")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{name}.svg").write_text("".join(out))
    print("wrote", name)


def arrow(x0, y0, x1, y1, colour="#202122"):
    def f(c):
        return (f'<path d="M{x0*c:.1f} {y0*c:.1f}L{x1*c:.1f} {y1*c:.1f}" stroke="{colour}" stroke-width="1.6" '
                f'marker-end="url(#a)" fill="none"/><defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{colour}"/></marker></defs>')
    return f


def brace(x0, x1, y, text):
    def f(c):
        return (f'<path d="M{x0*c:.1f} {y*c-4:.1f}v4H{x1*c:.1f}v-4" stroke="#54595d" stroke-width="1.3" fill="none"/>'
                f'<text x="{(x0+x1)/2*c:.1f}" y="{y*c+13:.1f}" text-anchor="middle" font-size="11.5" fill="#54595d">{text}</text>')
    return f


def main():
    # 1. Reach: a stone brick shelf vs a log beam off the same wall.
    diagram("reach", [
        "..................",
        "BBBBBx............",
        "B.................",
        "B.................",
        "B.................",
        "BLLLLLLLLLLLLl....",
        "B.................",
        "GGGGGGGGGGGGGGGGGG",
        "DDDDDDDDDDDDDDDDDD",
    ], title="A stone brick shelf falls once its reach runs out; a log beam carries twelve blocks out",
       notes=[(0.1, 0.6, "Stone bricks: reach 4. The 5th block out falls.", "start"),
              (1.2, 4.6, "Logs: reach 12. The 13th block out falls.", "start")])

    # 2. The carrier decides: stone on the end of a timber beam vs stone off stone.
    diagram("carrier", [
        "......................",
        "L.........B...........",
        "LLLLLLLLLLL...........",
        "L.....................",
        "L...........CCCx......",
        "L...........C.........",
        "L...........C.........",
        "GGGGGGGGGGGGGGGGGGGGGG",
    ], title="Stone resting on a timber beam is held by the beam; a cobblestone shelf runs out after two blocks",
       notes=[(0.2, 0.7, "Stone on a log beam: held", "start"),
              (12, 3.6, "Cobble off cobble: 2 blocks, then it falls", "start")])

    # 3. Arch: two-sided support.
    diagram("arch", [
        "....................",
        "..BBBBBBBBBBBBBBBB..",
        "..BBB..........BBB..",
        "..BB............BB..",
        "..B..............B..",
        "..B..............B..",
        "GGGGG~~~~~~~~~~GGGGG",
        "DDDDD~~~~~~~~~~DDDDD",
    ], title="A masonry arch: each half helps hold up the middle",
       notes=[(10, 0.7, "Held from both ends, the span reaches further", "middle")],
       marks=[arrow(4, 3.4, 7.5, 1.9, "#2f6446"), arrow(16, 3.4, 12.5, 1.9, "#2f6446")])

    # 4. Hanging: chain vs stone.
    diagram("hanging", [
        "..............",
        "LLLLLLLLLLLLLL",
        "L...K.....B..L",
        "L...K.....b..L",
        "L...K........L",
        "L...T........L",
        "L............L",
        "GGGGGGGGGGGGGG",
    ], title="A lantern hangs from a chain; stone can barely hang anything",
       notes=[(5.2, 5.6, "Chain: hang 12", "start"), (10.5, 5.2, "Stone: hang 1", "middle")])

    # 5. Cave-ins, seen from ABOVE: width is what matters.
    diagram("mine", [
        "RRRRR...................RRRR",
        "R..........RRRRRRRRRRRRRRRRR",
        "RRRRR...................RRRR",
        "RRRRR...................RRRR",
        "RRRRR.......RRRRR.......RRRR",
        "RRRRR...o...RRRRR.......RRRR",
        "RRRRR...................RRRR",
        "RRRRR...o...RRRRR.......RRRR",
        "RRRRR.......RRRRR.......RRRR",
        "RRRRR...................RRRR",
    ], title="Mine plan seen from above: a one-wide tunnel is safe, a braced room is safe, a wide unbraced room risks a cave-in",
       notes=[(1, 1.75, "1-wide tunnel: always safe", "start"),
              (8.5, 10.7, "Room braced by posts", "middle"),
              (20.5, 10.7, "Wide, no posts: cave-in risk", "middle")],
       marks=[lambda c: f'<rect x="{17*c}" y="{4*c}" width="{7*c}" height="{5*c}" fill="rgba(210,50,40,.2)" stroke="#d2322a" stroke-width="2" stroke-dasharray="5 4"/>'])

    # 6. Ships: wooden hull, wool sail in the top 30%.
    diagram("ship-sail", [
        "......WWWWLWWWW......",
        "......WWWWLWWWW......",
        "......WWWWLWWWW......",
        "..........L..........",
        "..........L..........",
        "..........L..........",
        "..........L..........",
        "PP........L........PP",
        "PPPPPPPPPPPPPPPPPPPPP",
        ".PPPPPPPPPPPPPPPPPPP.",
        "~~PPPPPPPPPPPPPPPPP~~",
        "~~~~~~~~~~~~~~~~~~~~~",
    ], title="A ship: wooden hull below, wool sail in the top 30% of her height",
       bands=[(0, 3, "rgba(47,100,70,.14)", "top 30%: sail zone")],
       notes=[(0.2, 1.7, "Wool up here counts", "start"), (0.2, 6.6, "Hull: at least half wood", "start")])


if __name__ == "__main__":
    main()
