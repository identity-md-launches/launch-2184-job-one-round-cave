# The Watchful Window — seventh gathering

[Window Review](../shared/window-review/README.md) connects verified incident
window queries to printable review of original log evidence. Offline, Python
3.10+ standard library only:

```sh
python3 -B shared/window-review/window_review.py demo
```

Observed synthetic result: two possible overlaps, one outside event, one undated
duplicate-key JSON line. Hidden direction controls remain visible as escaped
evidence. Unshown/outside evidence is explicitly unreviewed. Original spans,
hashes, BOM/CRLF handling, query totals and truncation are labeled. Twelve
integration tests passed, including an isolated copied-folder CLI.

[REPORT.md](REPORT.md) covers all four lines and all 21 tools, observed behavior,
limits and scope for 21 Pepes. **382 tests and 39 CLI checks passed.** All line
folders/records remain unchanged. [COINS.md](COINS.md) says none: no capability
requires a new coin, payment or pool.

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
python3 -B gathering/verify.py
python3 -B gathering/check_gallery.py
```

Wall: `artifacts/gathering/wall-v7.png`, **1254 × 1254 RGB8 PNG**.
Preview: `dist/gathering/07.jpg`, **512 × 512 baseline JPEG, 97,373 bytes**.
The added chalk eye is pigment from built-in imagegen. Exactly 1,503 pixels
change from gathering 06; every pixel outside the added pigment remains exact.
Pepe's inherited hands retain five digits each. No new hands, letters or numbers.
Both outputs were locally inspected; no unmet visual requirement observed.
The worn eye is faint at preview size; independent approval is not claimed.
[image-prompt.txt](image-prompt.txt) contains the full final prompt;
`mark-process.json` and `wall-review.json` record processing and review.
`add_mark7.js` isolates generated pigment. It must only run against the original
generated donor, not the already finished output; it is not an image generator.

`dist/gathering/07.json` and `dist/one.json` use the actual PNG hash.
`dist/goals.json` copies the four exact goals. `dist/index.html` lists all 126
records, painted newest first by wall, then future slots. It needs no external
scripts, styles or fonts. Full PNG links need the artifact service. Earlier
records and future placeholders are retained.

Rebuild preview and gallery:

```sh
python3 -B gathering/make_preview.py artifacts/gathering/wall-v7.png dist/gathering/07.jpg
python3 -B gathering/build_dist.py
```

`wall.png` is a relative alias of the required named PNG, which stays untracked
for separate artifact upload. Structural checks cover bytes, paths and ordering;
they do not certify browser rendering or scientific claims.
