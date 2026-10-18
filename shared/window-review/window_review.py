#!/usr/bin/env python3
"""Review original evidence behind a verified time-window query, as inert ASCII."""
import argparse
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / 'engines/timeline-window'))
import timeline_window as window

spec = importlib.util.spec_from_file_location(
    'review_unicode_window', HERE / 'engines/unicode-window/unicode_window.py')
unicode = importlib.util.module_from_spec(spec)
spec.loader.exec_module(unicode)
lantern = unicode.replay.citations.lantern.lantern
MAX_OUTPUT = 4 * 1024 * 1024
MAX_LINES = 50
MAX_FINDINGS = 20
PREVIEW_BYTES = 256


def quoted(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, allow_nan=False)


def original_lines(pack, wanted):
    """Map only selected citations; offsets refer to whole original source bytes.

    Match Time Flint's LF/BOM/CR policy, while retaining the exact physical bytes
    (including BOM and CR) in the separately labeled original span.
    """
    found = {}
    for item in pack['inputs']:
        name = item['source']
        if not any(source == name for source, _ in wanted):
            continue
        raw = base64.b64decode(item['base64'], validate=True)
        offset = 0
        for number, physical in enumerate(raw.split(b'\n'), 1):
            if (name, number) in wanted:
                start = offset
                payload = physical
                if number == 1 and payload.startswith(b'\xef\xbb\xbf'):
                    payload = payload[3:]
                    start += 3
                payload = payload.removesuffix(b'\r')
                found[name, number] = (offset, physical, start, payload, item['sha256'])
            offset += len(physical) + 1
    if set(found) != wanted:
        raise ValueError('verified citation has no original physical line')
    return found


def render(raw, start, end, limit=10, expected=None):
    if type(limit) is not int or not 0 <= limit <= MAX_LINES:
        raise ValueError('limit must be an integer in 0..50')
    if type(raw) is not bytes or len(raw) > window.replay.MAX_PACK_BYTES:
        raise ValueError('pack must be bytes within 16 MiB')
    digest = hashlib.sha256(raw).hexdigest()
    if expected is not None:
        if type(expected) is not str or window.HEX.fullmatch(expected) is None or expected != digest:
            raise ValueError('pack differs from independently retained SHA-256')
    pack = window.replay.load_pack(raw)
    query = window.inspect(pack, start, end, limit)  # Complete replay before review.
    selected = [(x['classification'], x['event']) for x in query['events']]
    selected += [('undated; time unknown', x) for x in query['undated_lines']]
    wanted = {(x['source'], x['line']) for _, x in selected}
    originals = original_lines(pack, wanted)
    lines = ['WINDOW REVIEW / 1', 'Pack exact-byte SHA-256: ' + digest,
             'Independent digest checked: ' + str(expected is not None).lower(),
             'Query: ' + quoted(query['query']), 'Counts: ' + quoted(query['counts']),
             'Clock assumptions: ' + quoted(query['options']),
             'Only shown matching events and shown undated lines are scanned.',
             'Outside-window events, blank lines and unshown details are NOT reviewed.',
             'No findings is not a safety verdict. Evidence is not redacted.',
             'Original spans: zero-based half-open whole-source bytes, excluding LF.',
             'Payload strips initial BOM and trailing CR; add payload start to JSON-local spans.',
             'Byte previews double backslashes; other nonprintable/non-ASCII bytes use \\xHH.',
             'Quoted fields use JSON notation; never unescape before terminal display.']
    for classification, item in selected:
        name, number = item['source'], item['line']
        offset, physical, payload_start, payload, source_hash = originals[name, number]
        lines += ['', 'CITATION ' + quoted({'source': name, 'line': number}),
                  'Classification: ' + classification,
                  'Whole-source SHA-256: ' + source_hash,
                  'Original physical span: [%d,%d); SHA-256: %s' % (
                      offset, offset + len(physical), hashlib.sha256(physical).hexdigest()),
                  'Original preview: ' + unicode.byte_text(physical[:PREVIEW_BYTES]),
                  'Original preview bytes omitted: ' + str(max(0, len(physical) - PREVIEW_BYTES)),
                  'Payload span: [%d,%d); SHA-256: %s' % (
                      payload_start, payload_start + len(payload), hashlib.sha256(payload).hexdigest())]
        if classification.startswith('undated'):
            lines.append('Omission reason: ' + quoted(item['reason']))
        else:
            lines.append('Verified event: ' + quoted(item))
        if payload.decode('utf-8').lstrip().startswith('{'):
            try:
                review = unicode.render(unicode.replay.pack(payload, MAX_FINDINGS))
            except (ValueError, RecursionError, OverflowError) as exc:
                # An omitted malformed JSON line is unknown, never silently clean.
                lines.append('JSON REVIEW INCOMPLETE: ' + quoted(str(exc)))
            else:
                lines += ['JSON review coordinates are LOCAL TO PAYLOAD:', review.rstrip('\n')]
        else:
            scan = lantern.scan(payload, '<physical-line>', MAX_FINDINGS)
            lines.append('Raw-text review: ' + quoted(scan))
    lines += ['', 'LIMITS: Replay establishes consistency, not log truth, completeness or authorship.',
              'A digest from the untrusted pack supplies no independent authentication.',
              'Clock bounds are analyst assertions; temporal overlap is not causality.',
              'Unicode detection is the inherited limited Latin/Greek/Cyrillic heuristic.',
              'Raw-text offsets are payload-local; JSON findings can include decoded-string coordinates.',
              'Counts describe the query, not the number of unique attacks or affected events.']
    result = '\n'.join(lines) + '\n'
    if len(result) > MAX_OUTPUT:
        raise ValueError('review exceeds 4 MiB; lower --limit')
    if any(c != '\n' and not 32 <= ord(c) <= 126 for c in result):
        raise ValueError('ASCII output contract violated')
    return result


def demo_pack():
    return window.replay.make_pack([
        ('queue.jsonl', b'\xef\xbb\xbf' +
         br'{"ts":1792317602000,"message":"hidden \u202eevil\u202c"}' + b'\r\n' +
         br'{"owner":1,"owner":2,"note":"\u200b"}' + b'\r\n'),
        ('service.log', b'2026-10-18T10:00:00Z outside\n2026-10-18T10:00:03Z completed\n')
    ], ignore_unmatched=True, clock_uncertainty_ms=250)


def main(argv=None):
    cli = argparse.ArgumentParser(description=__doc__)
    actions = cli.add_subparsers(dest='command', required=True)
    actions.add_parser('demo', help='synthetic evidence; no independent authenticity pin')
    review = actions.add_parser('review')
    review.add_argument('pack', help='explicit existing workspace Timeline Replay pack')
    review.add_argument('--start', required=True)
    review.add_argument('--end', required=True)
    review.add_argument('--limit', type=int, default=10)
    review.add_argument('--expect-sha256', help='independently trusted exact-byte pack digest')
    args = cli.parse_args(argv)
    try:
        if args.command == 'demo':
            text = 'SYNTHETIC DEMONSTRATION; NOT A REAL INCIDENT\n' + render(
                window.replay.canonical(demo_pack()), '2026-10-18T10:00:02Z', '2026-10-18T10:00:04Z')
        else:
            raw = window.replay.read_workspace(args.pack, window.replay.MAX_PACK_BYTES)
            text = render(raw, args.start, args.end, args.limit, args.expect_sha256)
        sys.stdout.write(text)
        return 0
    except (OSError, ValueError, TypeError, RecursionError, OverflowError) as exc:
        sys.stderr.write('window-review: ' + quoted(str(exc)) + '\n')
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
