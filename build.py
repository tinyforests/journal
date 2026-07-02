#!/usr/bin/env python3
"""
Gardener & Son — Garden Journal builder.

Usage:
    python3 build.py data/<slug>.json

Reads a project JSON file and writes output/<slug>.html — a single
self-contained, static page in the G&S design system. No dependencies
beyond the standard library.
"""
import json
import sys
import html
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent


def esc(s):
    return html.escape(s or "", quote=True)


def fmt_date(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%-d %B %Y")


def fmt_date_short(iso):
    d = datetime.strptime(iso, "%Y-%m-%d")
    return d.strftime("%d.%m.%y")


def render_photo(photo):
    caption = esc(photo.get("caption", ""))
    src = photo.get("src")
    if src:
        img_tag = f'<img src="{esc(src)}" alt="{caption}" loading="lazy" onclick="openLightbox(this.src)">'
    else:
        # Placeholder — no photo file supplied yet
        img_tag = (
            '<div class="photo-placeholder">'
            '<svg viewBox="0 0 24 24" width="28" height="28" aria-hidden="true">'
            '<circle cx="12" cy="12" r="10" fill="none" stroke="currentColor" stroke-width="1"/>'
            '<circle cx="12" cy="12" r="5.5" fill="none" stroke="currentColor" stroke-width="1"/>'
            '</svg>'
            '<span>photo pending</span>'
            '</div>'
        )
    return f'<figure class="photo">{img_tag}<figcaption>{caption}</figcaption></figure>'


def render_entry(entry, index, total):
    date_long = fmt_date(entry["date"])
    date_short = fmt_date_short(entry["date"])
    title = esc(entry["title"])
    body = esc(entry["body"]).replace("\n\n", "</p><p>")
    photos = entry.get("photos", [])
    photos_html = "".join(render_photo(p) for p in photos)
    photos_block = f'<div class="entry-photos">{photos_html}</div>' if photos else ""
    is_latest = " is-latest" if index == 0 else ""
    ring = index + 1

    return f"""
    <article class="entry{is_latest}">
      <div class="entry-marker">
        <span class="ring" style="--ring:{ring}"></span>
      </div>
      <div class="entry-body">
        <div class="entry-meta">
          <time class="entry-date" datetime="{entry['date']}">{date_long}</time>
          <span class="entry-date-short">{date_short}</span>
        </div>
        <h3 class="entry-title">{title}</h3>
        <p>{body}</p>
        {photos_block}
      </div>
    </article>"""


def build(data_path):
    data = json.loads(Path(data_path).read_text())
    slug = data["slug"]
    project_name = esc(data["project_name"])
    client_name = esc(data.get("client_name", ""))
    address = esc(data.get("address", ""))
    designer = esc(data.get("designer", ""))
    status = esc(data.get("status", "In progress"))
    indexed_entries = list(enumerate(data["entries"]))
    indexed_entries.sort(key=lambda pair: (pair[1]["date"], pair[0]), reverse=True)
    entries = [e for _, e in indexed_entries]
    entries_count = len(entries)
    started = fmt_date(data["start_date"]) if data.get("start_date") else ""
    latest_date = fmt_date(entries[0]["date"]) if entries else ""

    entries_html = "".join(
        render_entry(e, i, entries_count) for i, e in enumerate(entries)
    )

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light only">
<meta name="theme-color" content="#fff0dc">
<title>{project_name} — Garden Journal — Gardener &amp; Son</title>
<meta name="description" content="A running record of the {project_name} garden install, by Gardener &amp; Son.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,400&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    color-scheme: light;
    --green: #3d4535;
    --beige: #fff0dc;
    --brass: #B49A63;
    --ink: #2a2a22;
    --line: rgba(61,69,53,0.18);
    --paper: #fffaf1;
  }}

  * {{ box-sizing: border-box; }}

  html {{ scroll-behavior: smooth; }}

  body {{
    margin: 0;
    background: var(--beige);
    background-image:
      radial-gradient(rgba(61,69,53,0.035) 1px, transparent 1px);
    background-size: 3px 3px;
    color: var(--ink);
    font-family: 'IBM Plex Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
  }}

  a {{ color: var(--green); }}

  .wrap {{
    max-width: 760px;
    margin: 0 auto;
    padding: 0 24px 120px;
  }}

  /* ---------- Header ---------- */
  header.hero {{
    padding: 64px 0 40px;
    border-bottom: 1px solid var(--line);
    margin-bottom: 56px;
  }}

  .eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--green);
    opacity: 0.75;
    margin: 0 0 18px;
  }}

  .eyebrow .dot {{
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--brass);
    margin-right: 8px;
    vertical-align: middle;
  }}

  h1.project-name {{
    font-family: 'Abril Fatface', serif;
    font-weight: 400;
    font-size: clamp(38px, 7vw, 58px);
    line-height: 1.04;
    color: var(--green);
    margin: 0 0 22px;
  }}

  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 18px 32px;
    padding-top: 22px;
    border-top: 1px solid var(--line);
  }}

  .meta-item .label {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10.5px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--green);
    opacity: 0.6;
    margin-bottom: 4px;
  }}

  .meta-item .value {{
    font-family: 'Fraunces', serif;
    font-size: 16px;
    color: var(--ink);
  }}

  /* ---------- Timeline ---------- */
  .timeline {{
    position: relative;
  }}

  .timeline::before {{
    content: "";
    position: absolute;
    left: 19px;
    top: 8px;
    bottom: 8px;
    width: 1px;
    background: var(--line);
  }}

  .entry {{
    position: relative;
    display: grid;
    grid-template-columns: 40px 1fr;
    gap: 8px 28px;
    margin-bottom: 56px;
  }}

  .entry:last-child {{ margin-bottom: 0; }}

  .entry-marker {{
    position: relative;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding-top: 6px;
  }}

  .ring {{
    position: relative;
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 1px solid var(--green);
    background: var(--beige);
    z-index: 1;
  }}

  .entry.is-latest .ring {{
    background: var(--brass);
    border-color: var(--brass);
  }}

  .entry.is-latest .ring::before {{
    content: "";
    position: absolute;
    inset: -6px;
    border-radius: 50%;
    border: 1px solid var(--brass);
    opacity: 0.5;
  }}

  .entry-meta {{
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 6px;
  }}

  .entry-date {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    letter-spacing: 0.05em;
    color: var(--green);
    opacity: 0.75;
  }}

  .entry.is-latest .entry-date {{
    color: var(--brass);
    opacity: 1;
    font-weight: 500;
  }}

  .entry-date-short {{ display: none; }}

  .entry-title {{
    font-family: 'Fraunces', serif;
    font-weight: 500;
    font-size: 23px;
    line-height: 1.25;
    color: var(--green);
    margin: 0 0 10px;
  }}

  .entry-body p {{
    margin: 0 0 14px;
    font-size: 15.5px;
    line-height: 1.65;
    color: var(--ink);
    max-width: 58ch;
  }}

  .entry-photos {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px;
    margin-top: 18px;
  }}

  figure.photo {{
    margin: 0;
    border: 1px solid var(--line);
    background: var(--paper);
  }}

  figure.photo img {{
    display: block;
    width: 100%;
    height: 150px;
    object-fit: cover;
    cursor: zoom-in;
  }}

  .photo-placeholder {{
    height: 150px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 8px;
    color: var(--green);
    opacity: 0.35;
  }}

  .photo-placeholder span {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }}

  figure.photo figcaption {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.02em;
    color: var(--ink);
    opacity: 0.7;
    padding: 8px 10px;
    border-top: 1px solid var(--line);
  }}

  /* ---------- Footer ---------- */
  footer {{
    margin-top: 80px;
    padding-top: 24px;
    border-top: 1px solid var(--line);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 11.5px;
    letter-spacing: 0.03em;
    color: var(--green);
    opacity: 0.6;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }}

  /* ---------- Lightbox ---------- */
  #lightbox {{
    display: none;
    position: fixed;
    inset: 0;
    background: rgba(42,42,34,0.92);
    z-index: 50;
    align-items: center;
    justify-content: center;
    padding: 32px;
    cursor: zoom-out;
  }}
  #lightbox.open {{ display: flex; }}
  #lightbox img {{
    max-width: 100%;
    max-height: 100%;
    border: 1px solid rgba(255,255,255,0.2);
  }}

  @media (prefers-reduced-motion: reduce) {{
    html {{ scroll-behavior: auto; }}
  }}

  @media (max-width: 480px) {{
    .wrap {{ padding: 0 16px 100px; }}
    header.hero {{ padding: 44px 0 28px; }}
    .entry {{ grid-template-columns: 28px 1fr; gap: 6px 16px; }}
    .ring {{ width: 12px; height: 12px; }}
    .timeline::before {{ left: 13px; }}
    .entry-date {{ display: none; }}
    .entry-date-short {{ display: inline; font-family: 'IBM Plex Mono', monospace; font-size: 12px; color: var(--green); opacity: 0.75; }}
  }}
</style>
</head>
<body>
<div class="wrap">

  <header class="hero">
    <p class="eyebrow"><span class="dot"></span>Garden Journal — {status}</p>
    <h1 class="project-name">{project_name}</h1>
    <div class="meta-grid">
      <div class="meta-item">
        <div class="label">Client</div>
        <div class="value">{client_name}</div>
      </div>
      <div class="meta-item">
        <div class="label">Address</div>
        <div class="value">{address}</div>
      </div>
      <div class="meta-item">
        <div class="label">Designer</div>
        <div class="value">{designer}</div>
      </div>
      <div class="meta-item">
        <div class="label">Started</div>
        <div class="value">{started}</div>
      </div>
      <div class="meta-item">
        <div class="label">Latest entry</div>
        <div class="value">{latest_date}</div>
      </div>
    </div>
  </header>

  <div class="timeline">
    {entries_html}
  </div>

  <footer>
    <span>Gardener &amp; Son — Ecological Design Studio</span>
    <span>{entries_count} entr{'y' if entries_count == 1 else 'ies'} logged</span>
  </footer>

</div>

<div id="lightbox" onclick="closeLightbox()">
  <img id="lightbox-img" src="" alt="">
</div>

<script>
  function openLightbox(src) {{
    document.getElementById('lightbox-img').src = src;
    document.getElementById('lightbox').classList.add('open');
  }}
  function closeLightbox() {{
    document.getElementById('lightbox').classList.remove('open');
  }}
  document.addEventListener('keydown', function(e) {{
    if (e.key === 'Escape') closeLightbox();
  }});
</script>

</body>
</html>
"""

    out_path = ROOT / "docs" / f"{slug}.html"
    out_path.write_text(html_out)
    print(f"Built {out_path}")


def build_index():
    data_dir = ROOT / "data"
    projects = []
    for f in sorted(data_dir.glob("*.json")):
        d = json.loads(f.read_text())
        latest = max(e["date"] for e in d["entries"]) if d["entries"] else d.get("start_date", "")
        projects.append({
            "slug": d["slug"],
            "name": d["project_name"],
            "address": d.get("address", ""),
            "status": d.get("status", "In progress"),
            "latest": latest,
            "count": len(d["entries"]),
        })
    projects.sort(key=lambda p: p["latest"], reverse=True)

    rows = ""
    for p in projects:
        rows += f"""
      <a class="row" href="{esc(p['slug'])}.html">
        <div class="row-main">
          <span class="row-name">{esc(p['name'])}</span>
          <span class="row-address">{esc(p['address'])}</span>
        </div>
        <div class="row-meta">
          <span class="row-status">{esc(p['status'])}</span>
          <span class="row-count">{p['count']} entries</span>
          <time class="row-date">{fmt_date_short(p['latest']) if p['latest'] else ''}</time>
        </div>
      </a>"""

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light only">
<meta name="theme-color" content="#fff0dc">
<title>Garden Journal — Gardener &amp; Son</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600&family=IBM+Plex+Sans:wght@400;500&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {{
    color-scheme: light;
    --green: #3d4535; --beige: #fff0dc; --brass: #B49A63;
    --ink: #2a2a22; --line: rgba(61,69,53,0.18); --paper: #fffaf1;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; background: var(--beige); color: var(--ink);
    font-family: 'IBM Plex Sans', sans-serif;
  }}
  .wrap {{ max-width: 760px; margin: 0 auto; padding: 64px 24px 100px; }}
  .eyebrow {{
    font-family: 'IBM Plex Mono', monospace; font-size: 12px; letter-spacing: 0.14em;
    text-transform: uppercase; color: var(--green); opacity: 0.75; margin: 0 0 18px;
  }}
  .eyebrow .dot {{ display:inline-block; width:6px; height:6px; border-radius:50%; background:var(--brass); margin-right:8px; vertical-align:middle; }}
  h1 {{
    font-family: 'Abril Fatface', serif; font-weight: 400;
    font-size: clamp(38px, 7vw, 58px); line-height: 1.04; color: var(--green); margin: 0 0 48px;
  }}
  .rows {{ border-top: 1px solid var(--line); }}
  .row {{
    display: flex; justify-content: space-between; align-items: baseline; gap: 16px;
    padding: 22px 0; border-bottom: 1px solid var(--line);
    text-decoration: none; color: inherit; flex-wrap: wrap;
  }}
  .row-main {{ display: flex; flex-direction: column; gap: 4px; }}
  .row-name {{ font-family: 'Fraunces', serif; font-weight: 500; font-size: 19px; color: var(--green); }}
  .row-address {{ font-family: 'IBM Plex Sans', sans-serif; font-size: 13px; opacity: 0.65; }}
  .row-meta {{ display: flex; gap: 14px; align-items: center; font-family: 'IBM Plex Mono', monospace; font-size: 11.5px; color: var(--green); opacity: 0.7; }}
  .row-status {{ text-transform: uppercase; letter-spacing: 0.06em; }}
</style>
</head>
<body>
<div class="wrap">
  <p class="eyebrow"><span class="dot"></span>Gardener &amp; Son</p>
  <h1>Garden Journal</h1>
  <div class="rows">{rows}
  </div>
</div>
</body>
</html>
"""
    out_path = ROOT / "docs" / "index.html"
    out_path.write_text(html_out)
    print(f"Built {out_path}")


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "all":
        for f in sorted((ROOT / "data").glob("*.json")):
            build(f)
        build_index()
    elif len(sys.argv) == 2:
        build(sys.argv[1])
        build_index()
    else:
        print("Usage: python3 build.py data/<slug>.json   (builds one project + refreshes index)")
        print("       python3 build.py all                (builds every project + index)")
        sys.exit(1)
