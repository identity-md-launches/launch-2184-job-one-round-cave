#!/usr/bin/env python3
"""Trace JSON Unicode findings back to exact original UTF-8 byte ranges."""

import argparse
from collections import defaultdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

DEPENDENCY = Path(__file__).resolve().parents[1] / "json-lantern" / "json_lantern.py"
spec = importlib.util.spec_from_file_location("citation_json_lantern", DEPENDENCY)
lantern = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lantern)
MAX_BYTES = lantern.MAX_BYTES
EXCERPT_BYTES = 96
DEMO = br'{"owner":1,"\u006fwner":2,"note":"\ud83d\udc38 hidden \u202eevil\u202c","a/b~":[{"pay-owner":0,"pay-\u043ewner":1}]}'


def location_key(location):
    return tuple(("index", part["index"]) if "index" in part else
                 (part["role"], part["pair"]) for part in location)


def string_tokens(raw):
    """Index string tokens in already validated JSON; duplicate keys stay distinct.

    Work in original bytes, so multibyte UTF-8 never shifts source citations.
    The ancestral review validates the grammar and budgets before this runs.
    """
    tokens = {}
    cursor = 0

    def whitespace():
        nonlocal cursor
        while cursor < len(raw) and raw[cursor] in b" \t\r\n":
            cursor += 1

    def string(path):
        nonlocal cursor
        start = cursor
        cursor += 1
        while raw[cursor] != 34:
            cursor += 2 if raw[cursor] == 92 else 1
        cursor += 1
        tokens[path] = (start, cursor)

    def value(path):
        nonlocal cursor
        whitespace()
        char = raw[cursor]
        if char == 34:
            string(path)
        elif char in (91, 123):
            cursor += 1
            whitespace()
            closing = 93 if char == 91 else 125
            index = 0
            if raw[cursor] != closing:
                while True:
                    if char == 123:
                        whitespace()
                        string(path + (("key", index),))
                        whitespace()
                        cursor += 1  # validated colon
                        child_path = path + (("value", index),)
                    else:
                        child_path = path + (("index", index),)
                    value(child_path)
                    whitespace()
                    if raw[cursor] == closing:
                        break
                    cursor += 1  # validated comma
                    index += 1
            cursor += 1
        else:
            while cursor < len(raw) and raw[cursor] not in b" \t\r\n,]}":
                cursor += 1

    value(())
    return tokens


def boundaries(raw, token, wanted):
    """Map selected decoded code-point boundaries to absolute source bytes.

    A surrogate pair is one decoded code point spanning twelve source bytes.
    Record only requested boundaries; never allocate a per-character index.
    """
    cursor, end = token[0] + 1, token[1] - 1
    decoded_index, found = 0, {}
    while True:
        if decoded_index in wanted:
            found[decoded_index] = cursor
        if cursor == end:
            break
        lead = raw[cursor]
        if lead == 92:
            if raw[cursor + 1] == 117:
                unit = int(raw[cursor + 2:cursor + 6], 16)
                width = 12 if 0xD800 <= unit <= 0xDBFF else 6
            else:
                width = 2
        else:
            width = 1 if lead < 0x80 else 2 if lead < 0xE0 else 3 if lead < 0xF0 else 4
        cursor += width
        decoded_index += 1
    if found.keys() != wanted:
        raise ValueError("finding points outside decoded string")
    return found


def evidence_length(evidence):
    # Only internally generated ASCII escape notation from Unicode Lantern.
    return len(evidence["escaped"].encode("ascii").decode("unicode_escape"))


def citation(raw, start, end):
    excerpt = raw[start:min(end, start + EXCERPT_BYTES)]
    # A byte excerpt is deliberately escaped byte-by-byte, including UTF-8.
    # It remains ASCII even after parsing the enclosing report JSON.
    escaped = "".join(chr(byte) if 32 <= byte <= 126 and byte != 92 else
                      "\\\\" if byte == 92 else f"\\x{byte:02x}" for byte in excerpt)
    return dict(byte_start=start, byte_end=end, bytes=end - start,
                sha256=hashlib.sha256(raw[start:end]).hexdigest(),
                excerpt_escaped_bytes=escaped, excerpt_truncated=end - start > EXCERPT_BYTES)


def review(raw, source="<memory>", max_findings=1000):
    report = lantern.review(raw, source, max_findings)
    tokens = string_tokens(raw)
    requests = defaultdict(set)
    work = []
    token_citations = {}

    def token_citation(key):
        if key not in token_citations:
            token_citations[key] = citation(raw, *tokens[key])
        return token_citations[key]

    for finding in report["findings"]:
        domain = finding["domain"]
        if domain == "decoded-string":
            key = location_key(finding["location"])
            finding["source_token"] = token_citation(key)
            for field, evidence in (("source_focus", finding["evidence"]),
                                    ("first_source_focus", finding["evidence"].get("first"))):
                if evidence is not None:
                    start = evidence["char_offset"]
                    end = start + evidence_length(evidence)
                    requests[key].update((start, end))
                    work.append((finding, field, key, start, end))
        elif domain == "object-key":
            finding["source_token"] = token_citation(location_key(finding["location"]))
            finding["first_source_token"] = token_citation(location_key(finding["first_location"]))
        else:
            for field, evidence in (("source_focus", finding["evidence"]),
                                    ("first_source_focus", finding["evidence"].get("first"))):
                if evidence is not None:
                    start = evidence["byte_offset"]
                    spelling = evidence["escaped"].encode("ascii").decode("unicode_escape")
                    finding[field] = citation(raw, start, start + len(spelling.encode("utf-8")))
    mapped = {key: boundaries(raw, tokens[key], wanted) for key, wanted in requests.items()}
    for finding, field, key, start, end in work:
        finding[field] = citation(raw, mapped[key][start], mapped[key][end])
    report.update(tool="json-citations", tool_version="1.0.0",
                  upstream_tool="json-lantern", upstream_version="1.0.0",
                  citation_contract="Zero-based half-open byte ranges in the original input. String tokens include quotes. Focus spans encode the original decoded finding, including entire escapes and surrogate pairs. Excerpts are ASCII byte notation, capped at 96 original bytes; hashes cover full spans.")
    report["limitations"].append("Citations locate inherited heuristic findings; they do not expand confusables coverage or prove intent. Input bytes must be preserved separately to verify citations.")
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--demo", action="store_true")
    group.add_argument("--file", help="explicit JSON file inside the current workspace")
    parser.add_argument("--max-findings", type=int, default=1000)
    args = parser.parse_args(argv)
    try:
        if args.demo:
            raw, source = DEMO, "<built-in-demo>"
        else:
            path = lantern.lantern.workspace_file(args.file)
            with path.open("rb") as handle:
                raw = handle.read(MAX_BYTES + 1)
            source = str(path.relative_to(Path.cwd().resolve()))
        result = review(raw, source, args.max_findings)
    except (OSError, ValueError, RecursionError) as error:
        print(json.dumps({"error": lantern.lantern.escaped(str(error))}, ensure_ascii=True))
        return 2
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if args.demo or not result["finding_count"] else 1


if __name__ == "__main__":
    sys.exit(main())
