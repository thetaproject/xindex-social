# xindex-social

Image and animation templates, and the rendered files, for Xindex posts on X and LinkedIn.
Every post is one visual: a still PNG or one animated GIF.

- `templates/` — 1200×675 layouts. Stills (rendered at 2×): `statement`, `steps`, `buildlog`, `stat`,
  `columns`, `poster`, `versus`, `chart`. Animations: `anim-site` (the xindex.io flow, see below) and
  `anim-index` (the earlier index-card animation).
- `specs/` — one JSON spec per post; `specs/examples/` shows the still templates, `specs/anim/` the animations.
- `posts/` — rendered files. Buffer attaches them by raw URL:
  `https://raw.githubusercontent.com/thetaproject/xindex-social/main/posts/<file>`.
  When a visual that is already attached to a draft changes, write it to a new file name (e.g. `-v2`), because
  Buffer and GitHub cache the old one.
- `render.py` — stills: `python3 render.py specs/<post>.json posts/<post>.png` (Chrome + `pip install jinja2`).
- `render_anim.py` — animations: `python3 render_anim.py specs/anim/<post>.json posts/<post>` writes `.gif`
  (under 9.5 MB), `.mp4` and a `.png` still (also needs `pip install playwright`; it uses the system Chrome).
- `assets/site/` — taken from the xindex.io site build: Figtree (SIL Open Font License), the Xindex logo,
  and the coin and stock icons the site shows (`assets/site/coins/<symbol>.png`, e.g. `btc`, `eth`, `nvdaon`,
  `xaut`, `aaplon`, `spyon`, `usdc.svg`).

## anim-site

The site's own flow, animated: the Create New Index basket card filling to 100%, the "What is an Index Coin?"
diagram (USDC fans out into the assets and joins into one index coin with a weight-coloured rim), and a
rebalance where weights drift and an open auction brings them back. Spec fields: `scenes` (any of
`create`, `buy`, `rebalance`), `assets` (`sym`, `name`, `icon`, `color`, `w`, `drift`; weights and drifts each
sum to 100), `headlines` and `steps` per scene (optional), `index_name`, `network`, `pay`, `pay_symbol`,
`inside_note`, `eyebrow`, `duration`, `still_t`. Example: `specs/anim/2026-11-30-index-coin-flow.json`.

## Brand

Taken from xindex.io: black ground, Figtree, white bold headlines with one accent phrase in `#3b82f6`,
grey sub copy `#9b9ba9`, cards `#0a0a14` with a 1px `#ffffff14` border, uppercase letter-spaced eyebrows,
dot-matrix spheres as decoration, asset colours BTC `rgb(247,147,26)`, ETH `rgb(190,200,230)`,
NVIDIA `rgb(118,185,0)`, gold `rgb(212,175,55)`.

Rules for anything rendered here: real facts only. No TVL, users, revenue, partners or audit claims;
numbers on `stat`, `versus` and `chart` need a citable `source`. Animated indexes are labelled illustrative.
