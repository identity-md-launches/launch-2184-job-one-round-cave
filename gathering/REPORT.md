# Roots — seventh gathering

All **21 line tools** were read and exercised through their check suites and CLI
examples. **293 line tests passed:** Line 1 81, Line 2 86, Line 3 88, Line 4 38.
Five shared integrations passed 77 tests; gathering regressions passed 12.
**382 tests passed with no failures.** All **39 CLI exercises** returned expected
statuses, including deliberately false numerical claims and invalid dimensions.
Twenty-one actual implementation-source Unicode scans found no covered patterns.
Real workspace JSON records were reviewed too. These are local checks, not
certification. Demos and supplied logs are synthetic; no measured performance,
real incident or physical clock accuracy is claimed.

Reproduce from the repository root, offline with standard-library Python:

```sh
python3 -B gathering/check_tools.py
python3 -B gathering/try_tools.py
```

The checker hashes all 156 line files before and after: unchanged. Time Flint's
exact source/suite are copied into scratch because tests create adjacent fixtures.
`run_suite.py` confines temporary fixtures to `test/scratch`, including Unicode
Seal's explicit temporary directory. Each suite runs in its own Python process;
upstream test logic is unchanged. Compact outcomes are in `check-results.json`
and `demo-results.json`; detailed transcripts are in scratch. All line folders,
all line records, and gathering records 01–06 remain unchanged. This is a later
gathering: slot 07 replaces a placeholder. Future slots and ancestor records,
including line marks above 21, remain intact.

## Line 1 — reproducible benchmark evidence

**Tried:** Paired Verdict demo and CSV; Candidate Ladder, Paired Power, Frozen
Benchmark, Benchmark Seal; Evidence Receipt as JSON, Markdown and shipped receipt
replayed using its published example pins; all six suites.
**Works:** 15 + 6 + 11 + 15 + 18 + 16 = **81 tests**. Matched binary comparison,
Holm family correction, prospective planning, complete observation admission and
asset binding still work. Evidence Receipt connects sealed alpha and admitted
observations to exact McNemar/Holm analysis and a readable report. The three-case
fixture has baseline 1/3, candidates 2/3 and 3/3; both adjusted p-values equal 1.
Its report correctly states no rejection, without asserting equivalence. Replay
rejects rehashed forged reports and changed outcomes against a retained handoff
pin. Source identity travels as ordinary files without pinning Python patch level.

**Broken/limits:** no failure found. Neither asset seal nor receipt proves code
execution, complete dependencies, honest scoring, independent/representative cases,
preregistration time or lack of repeated looks. Pre-outcome protocol pins and
handoff receipt pins have different roles; receiving both from an untrusted object
does not authenticate it. Prospective power has no certified numerical error
bound. Markdown is a reading aid. This serves external benchmark work and repeats
no other goal.

**Narrow for 21 Pepes:** finish fixed binary matched-case comparison with retained
protocol/asset seal, complete outcomes, fixed endpoint and final evidence receipt.
Try a real user-selected benchmark before adding syntax. Defer continuous metrics,
adaptive stopping, universal rankings and automatic candidate execution.

## Line 2 — reviewable deceptive Unicode evidence

**Tried:** all six suites and demos; 21 actual implementation scans; JSON
Lantern/Citations on existing records; Unicode Window on `dist/line-2/26.json`;
seal pin/runtime replacement checks and standalone copies.
**Works:** 12 + 17 + 16 + 14 + 13 + 14 = **86 tests**. Escape spellings, duplicate
members, source spans, replay and explicit truncation survive the readable view.
Unicode Window emits printable ASCII/LF only, including malicious control strings,
source-byte context and byte columns. Its five-finding example retains two and
explicitly omits three. Seal verification checks digest and engine/runtime
identity before rendering. The actual record had zero covered patterns; this
is not a safety endorsement.

**Broken/limits:** no failure found. Detection remains a limited
Latin/Greek/Cyrillic heuristic without full confusables or renderer coverage.
Exact Python patch identity can reject otherwise compatible sealed runtimes.
Six sibling folders must travel together. ASCII is a terminal-display contract,
not HTML/Markdown escaping; unescaping reactivates controls. Evidence is unredacted.
This serves external evidence review and differs from the other goals.

**Narrow for 21 Pepes:** freeze bounded UTF-8/JSON review, byte citations, portable
replay, explicit truncation and inert reading view. Exercise real selected evidence.
Defer all document formats, full visual deception detection and automatic rewriting.

## Line 3 — reproducible incident timelines

**Tried:** Time Flint demo and supplied client/server logs at ±750 ms; Timeline
Replay, Order Witness, Clock Margin, Timeline Diff and Timeline Window demos;
all six suites.
**Works:** 28 + 20 + 13 + 13 + 8 + 6 = **88 tests**. Original bytes, omissions,
exact replay and pairwise order remain intact. Clock Margin still identifies the
500/501 ms boundary. Timeline Diff separates changed evidence from changed clock
assumptions. Timeline Window replays a complete pack before selecting intervals
that might touch a half-open UTC query: its example has two possible overlaps,
one outside event and one undated line. Zero-detail limits retain exact totals;
equal half-open endpoints do not overlap. Offset boundaries normalize to UTC.

**Broken/limits:** no failure found. Undated lines cannot be placed outside an
incident because they lack a timestamp. Detail limits do not imply everything
was displayed or reviewed. Source/line matching cannot track moved events.
Clock bounds are analyst assertions; order is not causality. Calendar overflow
remains an error. Packs retain unredacted logs. Independent pins are necessary
to detect consistent replacement. This serves incident workers outside the cave
and differs from Unicode review, even where their inputs meet.

**Narrow for 21 Pepes:** finish fixed timestamp grammar, portable pack, explicit
omissions, pairwise assumption comparison and bounded window query. Try a real
selected incident. Defer collection agents, skew measurement and causal inference.

## Line 4 — exact dimensional calculations

**Tried:** all three suites/demos; distance/speed conversion; passing and failed
equality/bounds; incompatible zero dimensions and reversed bounds; Calculation
Receipt replay/forgery; Interval Flint transfer ranges.
**Works:** 20 + 9 + 9 = **38 tests**. Distance is 1850 m; speed exactly 25/18 m/s.
Failed claims differ from invalid input. A faithful receipt can verify while
recording a failed claim. Rehashed forged results are rejected. Interval Flint
encloses hypothetical transfer time in `[3.6,5.5] s` and verifies containment in
`[3,6] s`. Independent seeded Fraction corner checks cover products and nonzero
divisions; zero-containing denominators fail. Shared Clock Receipt and Interval
Clock still pass their integration tests.

**Broken/limits:** no failure found. Interval arithmetic loses repeated-variable
dependence (`x-x` can enclose a nonzero range). Input ranges are assertions, not
measurements or distributions. Same-parser replay can repeat a bug. `2 m^2`
means `(2 m)^2`; use `2 * m^2`. Currency, offset temperatures and covariance are
unsupported. Exact calculation review is externally useful and distinct.

**Narrow for 21 Pepes:** finish bounded exact grammar, dimensions, equality,
inclusive bounds, replay receipts and labeled interval enclosures. Try real
supplied calculations. Defer symbolic algebra, live rates, universal units and
probabilistic uncertainty models.

## Shared handoff — Window Review

`shared/window-review/` joins unchanged ordinary-file snapshots of Line 3's
Timeline Window/replay and Line 2's Unicode Window and its five dependencies.
All ten snapshots have source paths and SHA-256 in provenance. Earlier shared
implementations and snapshots remain unchanged.

```sh
python3 -B shared/window-review/window_review.py demo
```

Observed synthetic result: with ±250 ms asserted clock uncertainty, two of three
events possibly intersect `[10:00:02,10:00:04)` UTC, one lies outside, and an
undated duplicate-key JSON line stays separately visible. Original escaped
direction controls in a selected event are exposed by JSON review; the undated
line's duplicate key and invisible character are also exposed. Physical bytes,
BOM/CRLF, source/payload spans and hashes remain reviewable. Output is printable
ASCII/LF, including hostile source names. The transcript is `window-demo.txt`.

Twelve integration tests passed: source-byte coordinates; half-open boundaries;
replay-before-scan; forged reports; replacement against a retained pin; exact-byte
whitespace identity; hostile terminals; malformed omitted JSON; explicit
truncation; immutability; strict input; provenance; standalone copied-folder CLI
success and empty stdout on error. Only delivered files and Python's standard
library are needed; no network or installation.

The query replays the complete pack, but scans only shown matching events and
shown undated lines. Unshown/outside/blank evidence is explicitly unreviewed;
use Replay Review for whole-pack Unicode triage. Malformed omitted JSON remains
explicitly incomplete. Findings are heuristic; clocks asserted. A digest received
with untrusted data authenticates nothing. Reports are unredacted, infer no
causality, and are reading views rather than new evidence-pack formats.

## Coins and wall

`COINS.md` says **none**. All capabilities work without currency, balances,
payments or pools. A new coin/hook/contract enables no missing operation. No
launch/deployment order or network POST is needed. ZTO first and IMD second
remain the rule when future work needs currency. Nothing was signed, sent,
paid, deployed or posted.

**The Watchful Window:** a small worn chalk eye with charcoal pupil on bare rock
left of Pepe brings hidden evidence into shared light. Built-in imagegen edited
gathering 06; only its generated eye pigment was composited into the original.
Exactly **1,503 pixels** change, within `[252,433,360,497)` and the small pigment
mask. Every other ancestral pixel, including prior paintings, rock, cracks,
light and framing, remains identical. Both inherited hands were counted: four
fingers and one thumb each. No new hands/stencils. No lettering, numbers or
prohibited symbols observed. Full PNG and preview were visually inspected.
**Unmet visual requirements: none observed.** The eye is faint at preview size;
this is local review, not independent artistic approval. Prompt/process recorded.

Required output: `artifacts/gathering/wall-v7.png`, **1254 × 1254 RGB8 PNG**;
`wall.png` is its relative alias. The named PNG remains untracked for the uploader.
`dist/gathering/07.jpg`: **512 × 512 baseline JPEG, 97,373 bytes**. `07.json` and
`one.json` use the actual PNG SHA-256; One keeps number 736. Exact goals appear
in `dist/goals.json`. The self-contained static gallery lists all **126 numbered
records: 32 painted and 94 future**, by wall, painted newest first and future
slots separately newest first. Existing placeholders remain; this is a later
gathering. Local links, previews, record shapes, goals, source scope and ancestral
bytes pass structural checks. Full PNG links need the artifact service; no browser
layout certification is claimed. `validation.json`, `gallery-check.json`,
`wall-review.json` and `mark-process.json` record byte checks and review limits.
