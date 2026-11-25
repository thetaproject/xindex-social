#!/usr/bin/env python3
"""Render a XINDEX social image from a JSON spec.

Usage:  python3 render.py specs/2026-11-30.json posts/2026-11-30.png

The spec names a template in templates/ and fills its fields, e.g.
  {"template": "statement", "eyebrow": "Introducing Xindex",
   "headline": "Stocks, gold and crypto in <em>one token.</em>",
   "sub": "Up to 200 assets. Your weights. Backed in kind."}

Output is a 1200x675 frame rendered at 2x (2400x1350 PNG), which fits
X (16:9) and LinkedIn feed images.

Fonts: General Sans is not stored in this public repo (its licence is not
an open-source one). Put GeneralSans-Variable.woff2 in fonts/ before rendering;
without it the image falls back to the system sans.
"""
import json, os, pathlib, shutil, subprocess, sys, tempfile
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = pathlib.Path(__file__).resolve().parent
TEMPLATES = ["statement", "steps", "buildlog", "stat", "columns"]


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
    if tpl == "stat" and not spec.get("source"):
        sys.exit("stat template needs a 'source' (real, citable number only)")
    if not (ROOT / "fonts" / "GeneralSans-Variable.woff2").exists():
        print("WARNING: fonts/GeneralSans-Variable.woff2 missing - falling back to system sans", file=sys.stderr)
    env = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True)
    html = env.get_template(f"{tpl}.html").render(root=ROOT.as_uri(), **spec)
    out = pathlib.Path(out_path).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        page = pathlib.Path(td) / "page.html"
        page.write_text(html, encoding="utf-8")
        cmd = [find_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
               "--allow-file-access-from-files", "--force-device-scale-factor=2",
               "--window-size=1200,675", "--virtual-time-budget=3000",
               f"--screenshot={out}", page.as_uri()]
        subprocess.run(cmd, check=True, capture_output=True, timeout=120)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    render(sys.argv[1], sys.argv[2])
