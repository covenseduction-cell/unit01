#!/usr/bin/env python3
"""Builds the Settlers III wiki.

Each file in pages/ is an HTML fragment whose first line is a metadata comment:

    <!-- title: Ships & Sailing | group: Travel | order: 20 | status: live | summary: ... -->

Run `python3 build.py` and it writes one .html per page into the site root
(pages/home.html becomes index.html), plus search-index.json. Nothing to install.
"""
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
PAGES = ROOT / "pages"
SITE = "Settlers III Wiki"

GROUPS = ["Start here", "Maps", "Custom features", "The World", "Survival", "Building", "Travel", "Trade", "Reference"]
STATUS = {
    "live": ("Live", "Running on the server now."),
    "partial": ("Partly live", "Some of this is running now; the rest is still being built."),
    "planned": ("In development", "Designed, but not running on the server yet."),
}


def parse(path):
    text = path.read_text(encoding="utf-8")
    head, _, body = text.partition("\n")
    meta = dict(
        (k.strip(), v.strip())
        for k, v in (part.split(":", 1) for part in head.strip()[4:-3].split("|"))
    )
    slug = path.stem
    return {
        "slug": slug,
        "file": "index.html" if slug == "home" else f"{slug}.html",
        "title": meta["title"],
        "group": meta.get("group", "Reference"),
        "order": int(meta.get("order", 50)),
        "status": meta.get("status", ""),
        "summary": meta.get("summary", ""),
        "body": body,
    }


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def add_heading_ids(body):
    def repl(m):
        level, attrs, inner = m.group(1), m.group(2), m.group(3)
        if "id=" in attrs:
            return m.group(0)
        plain = re.sub(r"<[^>]+>", "", inner)
        return f'<h{level}{attrs} id="{slugify(html.unescape(plain))}">{inner}</h{level}>'
    return re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", repl, body, flags=re.S)


LIVE_MAP = "https://play.settlers-mc.org"
EXTERNAL = {"Maps": [("Live map \u2197", LIVE_MAP)]}


def nav(pages, current):
    out = []
    for g in GROUPS:
        items = sorted((p for p in pages if p["group"] == g), key=lambda p: (p["order"], p["title"]))
        if not items:
            continue
        out.append(f'<div class="nav-group"><div class="nav-heading">{g}</div><ul>')
        for p in items:
            cls = ' class="active" aria-current="page"' if p is current else ""
            out.append(f'<li><a href="{p["file"]}"{cls}>{html.escape(p["title"])}</a></li>')
        for label, url in EXTERNAL.get(g, []):
            out.append(f'<li><a href="{url}" target="_blank" rel="noopener">{html.escape(label)}</a></li>')
        out.append("</ul></div>")
    return "\n".join(out)


def badge(status):
    if status not in STATUS:
        return ""
    label, tip = STATUS[status]
    return f'<span class="status status-{status}" title="{tip}">{label}</span>'


def asset(path):
    digest = hashlib.sha1((ROOT / path).read_bytes()).hexdigest()[:10]
    return f"{path}?v={digest}"


def render(page, pages):
    title = page["title"] if page["slug"] == "home" else f'{page["title"]} · {SITE}'
    heading = "" if page["slug"] == "home" else (
        f'<header class="page-head"><div class="crumb">{page["group"]}</div>'
        f'<h1>{html.escape(page["title"])}</h1>'
        f'{badge(page["status"])}'
        + (f'<p class="lede">{page["summary"]}</p>' if page["summary"] else "")
        + "</header>"
    )
    desc = html.escape(re.sub(r"<[^>]+>", "", page["summary"]) or
                       "The player guide to Settlers III, a slow, regional survival server set in Celtic Britain.")
    return f"""<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title if page["slug"] != "home" else SITE)}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="assets/icon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{asset('assets/style.css')}">
</head>
<body class="page-{page["slug"]}">
<a class="skip" href="#main">Skip to content</a>
<header class="topbar">
  <button class="menu-btn" aria-label="Open navigation" aria-expanded="false" aria-controls="sidebar">
    <svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 6h18M3 12h18M3 18h18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
  </button>
  <a class="brand" href="index.html"><img src="assets/icon.svg" alt="" width="28" height="28"><span>Settlers <b>III</b> Wiki</span><small>The Caeldun Isles</small></a>
  <div class="search">
    <input id="search" type="search" placeholder="Search the wiki" autocomplete="off" aria-label="Search the wiki">
    <div id="results" class="results" role="listbox" hidden></div>
  </div>
</header>
<div class="layout">
  <nav id="sidebar" class="sidebar" aria-label="Wiki pages">
{nav(pages, page)}
  </nav>
  <main id="main" class="content">
    <article>
{heading}
{add_heading_ids(page["body"])}
    </article>
    <footer class="foot">
      <p>Settlers III is a community Minecraft server. This wiki describes how the server's own plugins work; numbers come from the live configuration and can change as the world is tuned.</p>
    </footer>
  </main>
</div>
<script src="{asset('assets/wiki.js')}"></script>
<script src="{asset('assets/maps.js')}"></script>
</body>
</html>
"""


def main():
    pages = [parse(p) for p in sorted(PAGES.glob("*.html"))]
    for p in pages:
        (ROOT / p["file"]).write_text(render(p, pages), encoding="utf-8")
    index = []
    for p in pages:
        text = re.sub(r"</?(?:strong|b|em|i|code|kbd|a|span|mark)\b[^>]*>", "", p["body"])
        text = re.sub(r"<[^>]+>", " ", text)
        text = html.unescape(re.sub(r"\s+", " ", text)).strip()
        heads = [html.unescape(re.sub(r"<[^>]+>", "", h))
                 for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", p["body"], re.S)]
        index.append({"t": p["title"], "u": p["file"], "g": p["group"],
                      "s": html.unescape(re.sub(r"<[^>]+>", "", p["summary"])),
                      "h": heads, "x": text})
    (ROOT / "search-index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print(f"Built {len(pages)} pages.")


if __name__ == "__main__":
    main()
