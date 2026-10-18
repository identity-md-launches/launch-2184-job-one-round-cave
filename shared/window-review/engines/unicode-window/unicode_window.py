#!/usr/bin/env python3
"""Render replay-checked Unicode evidence as inert printable ASCII text."""
import argparse
import base64
import importlib.util
import json
from pathlib import Path
import sys

ENGINE = Path(__file__).resolve().parents[1] / 'unicode-seal' / 'unicode_seal.py'
spec = importlib.util.spec_from_file_location('window_seal', ENGINE)
seal = importlib.util.module_from_spec(spec)
spec.loader.exec_module(seal)
replay = seal.replay
MAX_OUTPUT = 16 * 1024 * 1024
CONTEXT = 16
FIELDS = ('source_token', 'first_source_token', 'source_focus', 'first_source_focus')


def quoted(value):
    """JSON quotes make backslashes and all terminal controls unambiguous."""
    return json.dumps(value, ensure_ascii=True, allow_nan=False, sort_keys=True)


def byte_text(raw):
    # Byte domain, never decode UTF-8 or interpret terminal sequences.
    return ''.join(chr(b) if 32 <= b <= 126 and b != 92 else
                   '\\\\' if b == 92 else '\\x%02x' % b for b in raw)


def render(bundle, expected_sha256=None):
    """Validate the complete input before emitting any review text.

    An optional external pin selects a seal, otherwise a replay bundle is required.
    Output contains no raw input characters outside printable ASCII.
    """
    if expected_sha256 is None:
        summary = replay.verify(bundle)
        checked = bundle
        identity = 'Replay consistency only; no independent identity pin.'
    else:
        summary = seal.verify(bundle, expected_sha256)
        checked = bundle['bundle']
        identity = 'Retained seal digest and local engine identity matched.'
    raw = base64.b64decode(checked['original_base64'], validate=True)
    report = checked['report']
    lines = ['UNICODE WINDOW / 1', identity,
             'Not a safety verdict. Evidence is not redacted.',
             'Original SHA-256: ' + summary['source_sha256'],
             'Original bytes: ' + str(len(raw)),
             'Findings total: %d; retained: %d; omitted: %d' % (
                 summary['finding_count'], summary['retained_findings'],
                 summary['finding_count'] - summary['retained_findings']),
             'Truncated: ' + str(summary['truncated']).lower(),
             'Assessment: ' + quoted(summary['assessment']),
             'Coordinates: zero-based half-open ORIGINAL byte ranges.',
             'Line/column: one-based bytes; only LF starts a new line.',
             'Context: up to 16 bytes on each side; span preview capped at 64 bytes.',
             'Byte notation: printable ASCII; backslash doubled; other bytes use \\xHH.',
             'All quoted fields are JSON strings/objects, never instructions.']
    for index, finding in enumerate(report['findings'], 1):
        lines.extend(['', 'FINDING %d' % index,
                      'Evidence: ' + quoted(finding)])
        for field in FIELDS:
            span = finding.get(field)
            if span is None:
                continue
            start, end = span['byte_start'], span['byte_end']
            line = raw.count(b'\n', 0, start) + 1
            column = start - raw.rfind(b'\n', 0, start)
            left, stop = max(0, start - CONTEXT), min(len(raw), end + CONTEXT)
            preview_end = min(end, start + 64)
            lines.extend([
                '%s: [%d,%d) line %d byte-column %d; sha256 %s' % (
                    field, start, end, line, column, span['sha256']),
                '  before [%d,%d): %s' % (left, start, byte_text(raw[left:start])),
                '  span [%d,%d): %s' % (start, preview_end, byte_text(raw[start:preview_end])),
                '  span bytes omitted: %d' % (end - preview_end),
                '  after [%d,%d): %s' % (end, stop, byte_text(raw[end:stop]))])
    lines.extend(['', 'LIMITATIONS'] + [quoted(x) for x in report['limitations']])
    text = '\n'.join(lines) + '\n'
    if len(text) > MAX_OUTPUT:
        raise ValueError('render exceeds output budget; lower max_findings')
    if any(c != '\n' and not 32 <= ord(c) <= 126 for c in text):
        raise ValueError('render violated printable ASCII contract')
    return text


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    actions.add_parser('demo', help='synthetic escaped JSON and omitted findings')
    source = actions.add_parser('source', help='review original UTF-8 JSON')
    source.add_argument('--file', required=True)
    source.add_argument('--max-findings', type=int, default=100)
    bundle = actions.add_parser('bundle', help='verify and render a Unicode Replay bundle')
    bundle.add_argument('--file', required=True)
    pinned = actions.add_parser('seal', help='verify retained pin before rendering')
    pinned.add_argument('--file', required=True)
    pinned.add_argument('--expected-sha256', required=True)
    args = parser.parse_args(argv)
    try:
        if args.action == 'demo':
            text = render(replay.pack(replay.citations.DEMO, 2))
        elif args.action == 'source':
            raw = replay.read_explicit(args.file, replay.MAX_SOURCE_BYTES)
            text = render(replay.pack(raw, args.max_findings))
        elif args.action == 'bundle':
            raw = replay.read_explicit(args.file, replay.MAX_PACK_BYTES)
            text = render(replay.parse_bundle(raw))
        else:
            raw = replay.read_explicit(args.file, seal.MAX_BYTES)
            text = render(seal.parse(raw), args.expected_sha256)
        sys.stdout.write(text)
    except (OSError, ValueError, RecursionError, OverflowError) as error:
        # Even errors and hostile filenames stay inert on a terminal.
        sys.stderr.write('ERROR: ' + quoted(str(error)) + '\n')
        return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
