# xindex-social

Image templates and the rendered images for Xindex posts on X and LinkedIn.

- `templates/` — five branded 1200×675 layouts (rendered at 2×): `statement`, `steps`, `buildlog`, `stat`, `columns`.
- `specs/` — one JSON spec per post (`specs/YYYY-MM-DD.json`); `specs/examples/` shows every template.
- `posts/` — the rendered PNGs. Buffer attaches them by their raw URL:
  `https://raw.githubusercontent.com/thetaproject/xindex-social/main/posts/<file>.png`
- `render.py` — `python3 render.py specs/2026-11-30.json posts/2026-11-30.png` (needs Chrome and `pip install jinja2`).

Brand tokens follow the Xindex design system: black ground, `#3b82f6` / `#60a5fa` accent words,
General Sans, 16px-radius cards with a 1px `rgba(255,255,255,0.08)` border, uppercase letter-spaced eyebrows.

Rules for anything rendered here: real facts only. No TVL, users, revenue, partners or audit claims;
numbers on the `stat` template need a citable `source`.
