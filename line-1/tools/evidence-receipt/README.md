# Evidence Receipt

Turn a sealed, complete fixed binary benchmark into a **readable evidence report
and portable replayable receipt**. This joins Benchmark Seal's asset verification
and complete-result admission directly to Candidate Ladder's exact two-sided
McNemar tests and Holm family correction. Alpha comes from the sealed plan;
there is no override that can silently change it at analysis time.

Python 3.10+ standard library only. No install, network or account is required.
From the repository root, one command shows a complete working example:

```sh
python3 -B line-1/tools/evidence-receipt/evidence_receipt.py demo
```

When tried, it verified the existing synthetic three-case pack, admitted every
planned observation, analyzed both candidates and replayed its own receipt before
printing Markdown. Baseline passes were 1/3; the two candidates passed 2/3 and
3/3. Both Holm-adjusted p-values were exactly 1: **no rejection, and no claim of
equivalence**. These are inherited synthetic fixtures, not measured systems.
The shipped `example-report.md` is that readable report.

## Use a real sealed benchmark

First freeze your protocol and seal the actual case/system bytes with the
predecessor Benchmark Seal tool. Retain its seal independently **before outcomes
are collected**. Collect all planned paired outcomes once at the fixed endpoint.
Pass your pack, complete CSV and original retained seal to:

```sh
python3 -B line-1/tools/evidence-receipt/evidence_receipt.py create --pack your-pack.json --results your-results.csv --expected-seal-sha256 YOUR_ORIGINAL_SEAL > receipt.json
```

The uppercase token is an instruction to supply your original 64-character
lowercase hexadecimal seal, not an example value. Inputs must be regular files
resolving inside the current working directory. Neither input is changed.
The entire operation completes before anything is written to stdout. Exit 0
means valid evidence, regardless of whether any comparison rejects; exit 2 means
invalid input with stderr and no partial stdout. Redirect stdout to a **new**
file, never an input file. Do not reuse a stale receipt after failure.

Retain the resulting `receipt_sha256` separately at handoff, then share the JSON
receipt with the four Python runtime files in this folder. The JSON retains:

- Original pack and observation bytes as base64, their byte digests, the original
  asset seal and normalized-CSV digest.
- Every case/system asset ID, byte size and hash; the frozen pass rule, versions,
  alpha and complete paired analysis.
- Byte identity of all four runtime sources and a digest of the entire receipt
  body, including the inputs and recomputed reports.

A recipient supplies **both independently retained pins** to `replay`:

```sh
python3 -B line-1/tools/evidence-receipt/evidence_receipt.py replay --receipt receipt.json --expected-seal-sha256 YOUR_ORIGINAL_SEAL --expected-receipt-sha256 YOUR_HANDOFF_RECEIPT_PIN --markdown
```

This verifies the pins and engine identity, admits the embedded observations
again, recomputes the statistical report, compares every field, and only then
prints Markdown. Omit `--markdown` for a compact JSON replay status. The receipt
pin binds observations at handoff; the pre-outcome seal binds the protocol and
assets. Reading either expected pin from the untrusted object under review
loses that independent protection. Receipt formatting is not significant;
embedded original input bytes and normalized JSON values are.

The shipped synthetic receipt can be replayed immediately using the exact
command in `example-replay.txt`. `demo --json` emits a fresh example receipt.
Engine source changes deliberately require the original files for old receipts;
copying this folder preserves byte identity. No Python patch version is pinned.

## Interpretation and boundaries

Markdown shows candidate passes, paired wins/losses, effect in percentage points,
exact Holm-adjusted fractions and the direction of any rejection. Rejection in
the baseline's direction is labeled **Evidence favors baseline**, never an
improvement. A non-rejection does not prove equivalence. The JSON additionally
retains unadjusted exact p-values, decimal displays and statistical assumptions.
Effect decimals are the predecessor engine's floating-point reading aids.
User labels are ASCII-escaped and entity-encoded so Markdown syntax, HTML,
links and invisible direction controls are displayed as inert text.

No tool can establish honest scoring, representative independent cases, execution
of the sealed bundles, complete dependencies, preregistration time or lack of
repeated looks from these files alone. A handoff digest is not a signature or
proof of authorship. The receipt and report are **unredacted**; review the assets
before sharing. Markdown is a reading aid, not the replay authority. Payloads
are never executed or extracted. This workflow does not need currency, prices,
balances or transactions, so no ZTO/IMD interaction is invented.

Each original input is capped at 2 MiB. Compact receipts are capped at 12 MiB;
base64 inflates original bytes. CSV/plan limits remain 1–10,000 cases and 2–16
candidates. Large human reports include one row per bound asset. Path guards
are not a sandbox against concurrent filesystem changes. The program explicitly
reads only requested workspace inputs and its own fixed shipped source files;
it reads no environment variables and invokes no subprocesses or network calls.

## Verification and provenance

```sh
python3 -B -m unittest discover -s line-1/tools/evidence-receipt -v
```

Sixteen tests passed when tried: standalone copied-folder CLI replay, failed-pin
empty stdout, report forgery after rehashing, boolean/integer confusion, changed
results against an old handoff pin, rehashed asset replacement against the old
seal, engine identity, complete membership, original-versus-normalized CSV,
duplicate JSON, schemas, byte budgets, hostile rendering, adverse direction,
input immutability and exact predecessor source identity. All 65 predecessor
tests also passed. These local checks provide no independent scientific or
visual certification.

`seal_engine.py`, `frozen_engine.py` and `ladder_engine.py` are **unchanged ordinary
source snapshots** of the predecessor engines. `provenance.json` names their
sources and hashes. They are included so this folder runs offline by itself;
no ancestor implementation was modified. The runtime hashes these copies and
its wrapper into each receipt. The test suite additionally compares snapshots
with the original source files when run in this repository.
