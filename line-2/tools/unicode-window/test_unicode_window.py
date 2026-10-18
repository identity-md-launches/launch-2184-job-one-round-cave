import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('window', HERE / 'unicode_window.py')
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)


class WindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (Path.cwd() / 'test/scratch').mkdir(parents=True, exist_ok=True)

    def test_demo_counts_and_evidence(self):
        text = w.render(w.replay.pack(w.replay.citations.DEMO, 2))
        self.assertIn('Findings total: 5; retained: 2; omitted: 3', text)
        self.assertIn('Truncated: true', text)
        self.assertIn('source_focus: [54,60)', text)
        self.assertIn('Replay consistency only', text)

    def test_hostile_terminal_bytes_never_render(self):
        raw = json.dumps({'note': '\x1b]52;c;X\x07\r\t\u202e\u200b'}).encode()
        text = w.render(w.replay.pack(raw))
        self.assertTrue(all(c == '\n' or 32 <= ord(c) <= 126 for c in text))
        self.assertNotIn('\x1b', text)
        self.assertNotIn('\u202e', text)
        self.assertIn('U+202E', text)

    def test_byte_notation_is_unambiguous(self):
        self.assertEqual(w.byte_text(b'\\x1b\x1b\n\xff'), r'\\x1b\x1b\x0a\xff')

    def test_original_spelling_preserved(self):
        escaped = w.render(w.replay.pack(br'{"x":"\u202e"}'))
        literal = w.render(w.replay.pack('{"x":"\u202e"}'.encode()))
        self.assertIn(r'\\u202e', escaped)
        self.assertIn(r'\xe2\x80\xae', literal)
        self.assertIn('source_focus: [6,12)', escaped)
        self.assertIn('source_focus: [6,9)', literal)

    def test_lf_and_multibyte_byte_columns(self):
        raw = '{\r\n"a":"é", "x":"\u202e"}'.encode()
        start = raw.index('\u202e'.encode())
        text = w.render(w.replay.pack(raw))
        self.assertIn('source_focus: [%d,%d) line 2 byte-column %d' % (
            start, start + 3, start - raw.rfind(b'\n', 0, start)), text)

    def test_long_span_explicit_omission(self):
        text = w.render(w.replay.pack(json.dumps({'x': 'a' * 200 + '\u202e'}).encode()))
        self.assertRegex(text, r'span bytes omitted: [1-9][0-9]+')

    def test_tampered_report_refused(self):
        b = w.replay.pack(w.replay.citations.DEMO)
        b['report']['findings'][0]['source_token']['byte_start'] += 1
        with self.assertRaises(ValueError):
            w.render(b)

    def test_seal_requires_retained_pin(self):
        s = w.seal.pack(w.replay.citations.DEMO)
        self.assertIn('Retained seal digest', w.render(s, w.seal.fingerprint(s)))
        other = w.seal.pack(b'{}')
        with self.assertRaises(ValueError):
            w.render(s, w.seal.fingerprint(other))
        with self.assertRaises(ValueError):
            w.render(s)

    def test_zero_findings_not_safety(self):
        text = w.render(w.replay.pack(b'{}'))
        self.assertIn('retained: 0; omitted: 0', text)
        self.assertIn('Not a safety verdict', text)

    def test_output_budget_fails_closed(self):
        with patch.object(w, 'MAX_OUTPUT', 1):
            with self.assertRaisesRegex(ValueError, 'output budget'):
                w.render(w.replay.pack(b'{}'))

    def test_cli_real_source_and_bad_json(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd() / 'test/scratch') as tmp:
            p = Path(tmp) / 'sample.json'
            p.write_bytes(b'{}')
            run = subprocess.run([sys.executable, '-B', str(HERE / 'unicode_window.py'),
                                  'source', '--file', str(p)], capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn(b'Findings total: 0', run.stdout)
            p.write_bytes(b'{')
            run = subprocess.run([sys.executable, '-B', str(HERE / 'unicode_window.py'),
                                  'source', '--file', str(p)], capture_output=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, b'')
            self.assertTrue(all(b == 10 or 32 <= b <= 126 for b in run.stderr))

    def test_standalone_copy_all_dependencies(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd() / 'test/scratch') as tmp:
            root = Path(tmp)
            for folder in ('unicode-window', 'unicode-seal', 'unicode-replay',
                           'json-citations', 'json-lantern', 'unicode-lantern'):
                shutil.copytree(HERE.parent / folder, root / folder)
            run = subprocess.run([sys.executable, '-B', str(root / 'unicode-window/unicode_window.py'),
                                  'demo'], cwd=root, capture_output=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn(b'Findings total: 5', run.stdout)

    def test_bundle_and_seal_cli(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd() / 'test/scratch') as tmp:
            root = Path(tmp)
            bundle = w.replay.pack(w.replay.citations.DEMO, 2)
            sealed = w.seal.pack(w.replay.citations.DEMO, 2)
            for action, value, extra in (
                    ('bundle', bundle, []),
                    ('seal', sealed, ['--expected-sha256', w.seal.fingerprint(sealed)])):
                p = root / (action + '.json')
                p.write_bytes(w.replay.canonical(value))
                run = subprocess.run([sys.executable, '-B', str(HERE / 'unicode_window.py'),
                                      action, '--file', str(p)] + extra, capture_output=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertIn(b'Findings total: 5; retained: 2; omitted: 3', run.stdout)
            run = subprocess.run([sys.executable, '-B', str(HERE / 'unicode_window.py'),
                                  'seal', '--file', str(p), '--expected-sha256',
                                  w.seal.fingerprint(w.seal.pack(b'{}'))], capture_output=True)
            self.assertEqual(run.returncode, 2)
            self.assertEqual(run.stdout, b'')

    def test_strict_outer_json(self):
        with self.assertRaises(ValueError):
            w.replay.parse_bundle(b'{"format":1,"format":2}')
        with self.assertRaises(ValueError):
            w.seal.parse(b'{"x":NaN}')


if __name__ == '__main__':
    unittest.main()
