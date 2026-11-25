#!/usr/bin/env python3
"""Render an animated Xindex post (GIF + MP4) from a JSON spec.

Usage:  python3 render_anim.py specs/anim/2026-12-02-how-an-index-is-made.json posts/2026-12-02-how-an-index-is-made

Writes <out>.gif (for X and LinkedIn, kept under 10 MB), <out>.mp4 (fallback)
and <out>.png (a still of the busiest moment, for checking).
The spec names an animated template in templates/ (e.g. "anim-index") and fills it.
The template must define window.render(t) that draws the frame at time t (seconds).
"""
import json, pathlib, subprocess, sys, tempfile, shutil
from jinja2 import Environment, FileSystemLoader
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent
FPS = 30          # capture rate (MP4)
GIF_FPS = 15      # GIF uses every second frame
GIF_MAX = 9.5e6   # LinkedIn via Buffer accepts GIFs up to 10 MB


def chrome():
    for n in ("google-chrome", "chromium", "chromium-browser"):
        p = shutil.which(n)
        if p:
            return p
    sys.exit("Chrome not found")


def main(spec_path, out_base):
    spec = json.loads(pathlib.Path(spec_path).read_text(encoding="utf-8"))
    tpl = spec["template"]
    if not tpl.startswith("anim-"):
        sys.exit("animated templates are named anim-*")
    if not (ROOT / "fonts" / "GeneralSans-Variable.woff2").exists():
        print("WARNING: fonts/GeneralSans-Variable.woff2 missing", file=sys.stderr)
    dur = float(spec.get("duration", 9.6))
    html = Environment(loader=FileSystemLoader(ROOT / "templates"), autoescape=True) \
        .get_template(f"{tpl}.html").render(root=ROOT.as_uri(), **spec)
    out = pathlib.Path(out_base).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as td:
        td = pathlib.Path(td)
        page_file = td / "page.html"
        page_file.write_text(html, encoding="utf-8")
        frames = td / "f"
        frames.mkdir()
        n = int(round(dur * FPS))
        with sync_playwright() as p:
            b = p.chromium.launch(executable_path=chrome(), args=["--allow-file-access-from-files", "--no-sandbox"])
            pg = b.new_page(viewport={"width": 1200, "height": 675}, device_scale_factor=1)
            pg.goto(page_file.as_uri())
            pg.wait_for_timeout(600)
            for i in range(n):
                pg.evaluate(f"render({i / FPS})")
                pg.screenshot(path=str(frames / f"{i:04d}.png"))
            pg.evaluate(f"render({spec.get('still_t', 4.6)})")
            pg.screenshot(path=str(out.with_suffix(".png")))
            b.close()
        mp4 = out.with_suffix(".mp4")
        tmp = td / "o.mp4"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "%04d.png"),
                        "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2:0:0:black", "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p",
                        "-movflags", "+faststart", str(tmp)], check=True)
        shutil.move(tmp, mp4)
        gif = out.with_suffix(".gif")
        for width, colors in ((1200, 128), (1200, 96), (1000, 96), (900, 64)):
            pal = td / "pal.png"
            vf = f"fps={GIF_FPS},scale={width}:-1:flags=lanczos"
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "%04d.png"),
                            "-vf", f"{vf},palettegen=max_colors={colors}:stats_mode=diff", str(pal)], check=True)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", str(frames / "%04d.png"),
                            "-i", str(pal), "-lavfi", f"{vf}[x];[x][1:v]paletteuse=dither=sierra2_4a:diff_mode=rectangle",
                            "-loop", "0", str(td / "o.gif")], check=True)
            size = (td / "o.gif").stat().st_size
            if size <= GIF_MAX:
                break
        shutil.move(td / "o.gif", gif)
    print(gif, f"{gif.stat().st_size/1e6:.1f} MB")
    print(mp4, f"{mp4.stat().st_size/1e6:.1f} MB")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
