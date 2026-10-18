# Timeline Window

Find all events whose verified time intervals might touch a chosen UTC window.
The tool replays a Timeline Replay evidence pack from its embedded exact log bytes
before answering. It uses half-open intervals and includes declared timestamp
precision plus the pack's asserted symmetric clock uncertainty. Events fully inside
the window are `contained`; events that merely intersect are `possible_overlap`.
Undated lines remain visible in a separate list, since they cannot be placed on a
timeline. Detail limits report exact counts of anything left out.

Copy this whole folder, including `vendor/`, to use it independently. Python 3.10+
standard library only. One command from the repository root shows it working:

```sh
python3 -B line-3/tools/timeline-window/timeline_window.py demo
```

Observed locally: a synthetic pack replays successfully; of three events, two
possibly overlap the two-second query window, one lies outside, and one undated
line is reported separately. Six focused tests passed, including an exact
half-open boundary, a forged timeline rejection, invalid windows, and visible
truncation counts.

For a pack already in the workspace:

```sh
python3 -B line-3/tools/timeline-window/timeline_window.py window path/to/pack.json --start 2026-10-18T10:00:00Z --end 2026-10-18T10:05:00Z
```

An optional `--expect-sha256` takes an independently trusted SHA-256 of the exact
pack file. Without that pin, verification establishes internal consistency with
the shipped parser, not source authenticity. The tool reads only the named pack
inside the current workspace, not log paths named inside it. It does not measure
clock error, infer causes, or claim that undated lines were outside the window.
