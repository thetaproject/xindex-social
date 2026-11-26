#!/usr/bin/env python3
"""Render a XINDEX social image from a JSON spec.

Usage:  python3 render.py specs/2026-11-30.json posts/2026-11-30.png

The spec names a template in templates/ and fills its fields, e.g.
  {"template": "statement", "eyebrow": "Introducing Xindex",
   "headline": "Stocks, gold and crypto in <em>one token.</em>",
   "sub": "Up to 200 assets. Your weights. Backed in kind."}

Output is a 1200x675 frame rendered at 2x (2400x1350 PNG), which fits
X (16:9) and LinkedIn feed images. The "carousel" template writes a 1080x1350
multi-page PDF (a LinkedIn document post) plus a PNG of its first slide.

Fonts: Figtree (SIL Open Font License), the font of xindex.io, ships in
assets/site/figtree-var-latin.woff2;
without it the image falls back to the system sans.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = pathlib.Path(__file__).resolve().parent
TEMPLATES = ["statement", "steps", "buildlog", "stat", "columns", "poster", "versus", "chart", "carousel"]


def find_chrome():
    for name in ("google-chrome", "chromium", "chromium-browser", "chrome"):
        p = shutil.which(name)
        if p:
            return p
    sys.exit("No Chrome/Chromium found on PATH")


def render(spec_path, out_path):
    spec = json.loads(pathlib.Path(spec_path).read_text(encoding="utf-8"))
    tpl = spec.get("template")
    if tpl not in TEMPLATES:
        sys.exit(f"template must be one of {TEMPLATES}, got {tpl!r}")
    if tpl in ("stat", "versus", "chart") and not spec.get("source"):
        sys.exit(f"{tpl} template needs a 'source' (real, citable numbers only)")
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
    out = pathlib.Path(out_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    chrome = find_chrome()
    base = [chrome, "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
            "--allow-file-access-from-files", "--virtual-time-budget=4000"]
    with tempfile.TemporaryDirectory() as td:
        page = pathlib.Path(td) / "page.html"
        if tpl == "carousel":
            # out_path is the PDF; a PNG of the first slide is written beside it as the cover/thumbnail
            if out.suffix != ".pdf":
                sys.exit("carousel output must be a .pdf")
            page.write_text(env.get_template("carousel.html").render(root=ROOT.as_uri(), **spec), encoding="utf-8")
            subprocess.run(base + ["--no-pdf-header-footer", f"--print-to-pdf={out}", page.as_uri()],
                           check=True, capture_output=True, timeout=180)
            first = dict(spec, slides=spec["slides"][:1])
            cover = pathlib.Path(td) / "cover.html"
            cover.write_text(env.get_template("carousel.html").render(root=ROOT.as_uri(), **first)
                             .replace("{{ '%02d' % loop.index }}", ""), encoding="utf-8")
            png = out.with_suffix(".png")
            subprocess.run(base + ["--force-device-scale-factor=1", "--window-size=1080,1350",
                                   f"--screenshot={png}", cover.as_uri()], check=True, capture_output=True, timeout=120)
            print(png)
        else:
            page.write_text(env.get_template(f"{tpl}.html").render(root=ROOT.as_uri(), **spec), encoding="utf-8")
            subprocess.run(base + ["--force-device-scale-factor=2", "--window-size=1200,675",
                                   f"--screenshot={out}", page.as_uri()], check=True, capture_output=True, timeout=120)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    render(sys.argv[1], sys.argv[2])
