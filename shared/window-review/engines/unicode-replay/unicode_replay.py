#!/usr/bin/env python3
"""Pack original JSON bytes with Unicode citations and replay them offline."""

import argparse
import base64
import binascii
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


ENGINE = Path(__file__).resolve().parents[1] / "json-citations" / "json_citations.py"
spec = importlib.util.spec_from_file_location("replay_citations", ENGINE)
citations = importlib.util.module_from_spec(spec)
spec.loader.exec_module(citations)
MAX_SOURCE_BYTES = citations.MAX_BYTES
MAX_REPORT_BYTES = 8 * 1024 * 1024
MAX_PACK_BYTES = 16 * 1024 * 1024
SOURCE_LABEL = "<embedded-source>"
FORMAT = "unicode-replay/1"


def canonical(value):
    """Type-sensitive JSON comparison: notably true differs from 1 and 1.0."""
    return json.dumps(value, ensure_ascii=True, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("ascii")


def report_for(raw, limit):
    report = citations.review(raw, SOURCE_LABEL, limit)
    if len(canonical(report)) > MAX_REPORT_BYTES:
        raise ValueError("review exceeds report byte budget; lower max_findings")
    return report


def pack(raw, max_findings=1000):
    report = report_for(raw, max_findings)
    bundle = dict(format=FORMAT, max_findings=max_findings,
                  original_base64=base64.b64encode(raw).decode("ascii"),
                  report=report)
    if len(canonical(bundle)) > MAX_PACK_BYTES:
        raise ValueError("bundle exceeds byte budget")
    return bundle


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate bundle member")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-finite bundle number")


def parse_bundle(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_PACK_BYTES:
        raise ValueError("bundle must be bytes within the bundle byte budget")
    text = raw.decode("utf-8", errors="strict")
    # Report locations may be deep, but never arbitrarily recursive.
    citations.lantern.check_depth(text)
    return json.loads(text, object_pairs_hook=unique_object,
                      parse_constant=reject_constant)


def verify(bundle):
    """Recompute everything; never trust a hash or range claimed by a report."""
    if type(bundle) is not dict or set(bundle) != {
            "format", "max_findings", "original_base64", "report"}:
        raise ValueError("invalid bundle members")
    if bundle["format"] != FORMAT:
        raise ValueError("unsupported bundle format")
    limit = bundle["max_findings"]
    if type(limit) is not int or not 1 <= limit <= 1000:
        raise ValueError("max_findings must be an integer between 1 and 1000")
    encoded = bundle["original_base64"]
    if type(encoded) is not str or len(encoded) > 4 * ((MAX_SOURCE_BYTES + 2) // 3):
        raise ValueError("invalid original byte encoding or size")
    try:
        raw = base64.b64decode(encoded, validate=True)
    except (ValueError, binascii.Error) as error:
        raise ValueError("invalid original base64") from error
    if base64.b64encode(raw).decode("ascii") != encoded:
        raise ValueError("noncanonical original base64")
    if len(canonical(bundle["report"])) > MAX_REPORT_BYTES:
        raise ValueError("recorded report exceeds byte budget")
    replay = report_for(raw, limit)
    if canonical(bundle["report"]) != canonical(replay):
        raise ValueError("recorded report does not match current engine replay")
    return dict(verified=True, format=FORMAT,
                source_sha256=hashlib.sha256(raw).hexdigest(), source_bytes=len(raw),
                finding_count=replay["finding_count"],
                retained_findings=len(replay["findings"]), truncated=replay["truncated"],
                assessment=replay["assessment"], unicode_version=replay["unicode_version"],
                meaning="Recorded review matches these embedded bytes under this engine; not authorship or safety.")


def read_explicit(path, budget):
    selected = citations.lantern.lantern.workspace_file(path)
    with selected.open("rb") as handle:
        raw = handle.read(budget + 1)
    if len(raw) > budget:
        raise ValueError("selected file exceeds byte budget")
    return raw


def demo():
    bundle = pack(citations.DEMO, max_findings=2)
    result = verify(parse_bundle(canonical(bundle)))
    # A synthetically falsified citation must fail even with unchanged input.
    bundle["report"]["findings"][0]["source_token"]["byte_start"] += 1
    try:
        verify(bundle)
    except ValueError:
        result["altered_citation_rejected"] = True
    else:
        raise ValueError("demo did not reject an altered citation")
    result["demo"] = "synthetic JSON with original escapes, duplicate keys and truncation"
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest="action", required=True)
    create = actions.add_parser("pack", help="write a bundle to stdout")
    create.add_argument("--file", required=True)
    create.add_argument("--max-findings", type=int, default=1000)
    replay = actions.add_parser("verify", help="replay an explicit bundle file")
    replay.add_argument("--file", required=True)
    actions.add_parser("demo", help="offline synthetic replay and tampering check")
    args = parser.parse_args(argv)
    try:
        if args.action == "pack":
            result = pack(read_explicit(args.file, MAX_SOURCE_BYTES), args.max_findings)
        elif args.action == "verify":
            result = verify(parse_bundle(read_explicit(args.file, MAX_PACK_BYTES)))
        else:
            result = demo()
        print(canonical(result).decode("ascii"))
    except (OSError, ValueError, RecursionError) as error:
        print(json.dumps({"error": citations.lantern.lantern.escaped(str(error))}, ensure_ascii=True))
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
