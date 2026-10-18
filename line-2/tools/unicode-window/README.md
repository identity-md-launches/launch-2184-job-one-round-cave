# Unicode Window

Inspect original JSON bytes or a replay-checked evidence handoff as printable
ASCII text, without rendering its bidirectional characters or terminal controls.
This is a human review view over the existing detectors, not a new detector.

From the repository root, Python 3.9+ and the standard library are enough:

```sh
python3 -B line-2/tools/unicode-window/unicode_window.py demo
```

The synthetic example has five findings, two retained and three explicitly
omitted. It displays duplicate-key spellings and the original six-byte escape
for a right-to-left override, with byte ranges, hashes and surrounding context.
No files or network access are needed for the demo.

Review an explicitly selected non-sensitive UTF-8 JSON document:

```sh
python3 -B line-2/tools/unicode-window/unicode_window.py source --file dist/line-2/25.json --max-findings 20
```

Or review a previously created Unicode Replay bundle:

```sh
python3 -B line-2/tools/unicode-window/unicode_window.py bundle --file line-2/review-bundle.json
```

For a Unicode Seal, use the `seal` command with `--file` and
`--expected-sha256` set to its actual independently retained digest. The tool
checks that pin, engine identity and complete replay before constructing the
view. It never silently computes a replacement pin. A replay bundle or direct
source view establishes consistency only; an untrusted pin authenticates nothing.
See [Unicode Seal](../unicode-seal/README.md) for preparing and retaining pins.

Every retained finding is included as JSON-quoted evidence, followed by source
span views. Each view shows the original half-open byte range and full-span
SHA-256, a one-based LF line/byte-column, up to 16 original bytes before and
after, and up to 64 bytes of the span. Omitted span bytes and omitted findings
are counted separately. LF alone starts a line; columns count bytes, not screen
cells or Unicode characters. The embedded decoded coordinates remain labeled
by the ancestral report and must not be confused with original source bytes.

Byte previews double literal backslashes and use `\xHH` for nonprintable or
non-ASCII bytes. Quoted evidence uses JSON escaping, a different explicitly
labeled notation. The output contains only ASCII 0x20–0x7e and LF. Input ESC,
CR, TAB, bidi controls and Unicode separators never reach the terminal as active
characters. Do not unescape the output before displaying it. This is plain text,
not HTML or Markdown escaping; quote it appropriately if embedding elsewhere.
Content remains untrusted and may contain misleading printable words.

Success exits 0 even with findings. Invalid JSON, replay mismatch, incorrect
pin, incompatible sealed engine or an exceeded limit exits 2, with escaped
stderr and no partial review on stdout. Usage errors use argparse's stderr.
Input bounds are inherited: 2 MiB original, 64 containers, 20,000 values,
1–1,000 retained findings, 8 MiB canonical report and 16 MiB replay bundle
(seals allow an additional 64 KiB). The view defaults to 100 retained findings
for direct source input and caps output at 16 MiB; a budget violation requires
a smaller retention limit, never a partial clean result. The entire report is
validated before rendering; this is not a constant-memory stream processor.

Copy all six sibling folders together: `unicode-window`, `unicode-seal`,
`unicode-replay`, `json-citations`, `json-lantern`, `unicode-lantern`. All are
ordinary standard-library Python sources with no runtime downloads. Only fixed
local code and the explicitly selected file within the current workspace are
read. The tool writes stdout/stderr only; it does not follow any paths carried
inside evidence. No environment variables, keys, wallets, network, signing,
payments, posting or transactions are used. Review output is not redacted.

When tried, all 14 new tests passed, including malicious terminal content,
original literal versus escaped UTF-8, byte columns after CRLF/multibyte text,
truncation, long spans, changed citations, wrong pins, strict JSON, output
budgets, CLI failures and an isolated six-folder copy. All 72 unchanged
ancestral tests passed too. The real `dist/line-2/25.json` produced zero covered
patterns; its review is retained in `line-2/round-26-real-review.txt`. The demo
and hostile examples are synthetic, not observed attacks. Detection remains
the limited inherited Latin/Greek/Cyrillic heuristic and is not complete UTS #39.

```sh
python3 -B -m unittest discover -s line-2/tools/unicode-window -v
```
