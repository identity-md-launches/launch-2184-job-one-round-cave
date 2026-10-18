import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import evidence_receipt as e

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCRATCH = ROOT / 'test' / 'scratch'


class ReceiptTests(unittest.TestCase):
    def setUp(self):
        self.receipt = e.demo_receipt()
        self.seal = self.receipt['body']['seal_check']['seal_sha256']
        self.pin = self.receipt['receipt_sha256']

    def replay(self, value, receipt_pin=None, seal_pin=None):
        return e.replay(e.canonical(value), seal_pin or self.seal, receipt_pin or self.pin)

    def repin(self, value):
        value['receipt_sha256'] = e.digest(e.canonical(value['body']))
        return value['receipt_sha256']

    def test_demo_and_raw_byte_identity(self):
        self.assertEqual(self.replay(self.receipt), self.receipt)
        body = self.receipt['body']
        self.assertEqual(body['results_bytes_sha256'], e.digest(e.unblob(body['results_b64'])))
        self.assertEqual(body['analysis']['paired_cases'], 3)
        self.assertEqual(body['analysis']['input_sha256'], body['seal_check']['observations']['normalized_csv_sha256'])
        self.assertFalse(any(x['familywise_reject_equal_discordance'] for x in body['analysis']['candidates']))

    def test_wrong_independent_pins(self):
        for seal, receipt in [('0'*64, self.pin), (self.seal, '0'*64)]:
            with self.assertRaises(e.InputError):
                self.replay(self.receipt, receipt, seal)

    def test_report_forgery_even_with_rehashed_handoff_pin(self):
        altered = copy.deepcopy(self.receipt)
        altered['body']['analysis']['baseline_passes'] = 3
        with self.assertRaisesRegex(e.InputError, 'replayed'):
            self.replay(altered, self.repin(altered))

    def test_boolean_integer_alias_rejected(self):
        altered = copy.deepcopy(self.receipt)
        altered['body']['analysis']['baseline_passes'] = True
        with self.assertRaisesRegex(e.InputError, 'replayed'):
            self.replay(altered, self.repin(altered))

    def test_consistent_result_replacement_requires_new_handoff_pin(self):
        body = self.receipt['body']
        rows = e.unblob(body['results_b64']).replace(b'unicode,0,1,1', b'unicode,0,0,0')
        replaced = e.make(e.unblob(body['pack_b64']), rows, self.seal)
        with self.assertRaisesRegex(e.InputError, 'handoff pin'):
            self.replay(replaced)
        # Pre-outcome asset seal alone intentionally does not freeze results.
        self.assertEqual(self.replay(replaced, replaced['receipt_sha256']), replaced)

    def test_rehashed_asset_replacement_still_rejected(self):
        pack = e.frozen.parse_json(e.unblob(self.receipt['body']['pack_b64']))
        pack['content']['cases'][0]['data_b64'] = e.seal.encode(b'forged')
        pack['seal_sha256'] = e.digest(e.canonical(pack['content']))
        with self.assertRaisesRegex(e.InputError, 'seal mismatch'):
            e.make(e.canonical(pack), e.unblob(self.receipt['body']['results_b64']), self.seal)

    def test_engine_identity(self):
        altered = copy.deepcopy(self.receipt)
        altered['body']['engines']['ladder_engine.py'] = '0'*64
        with self.assertRaisesRegex(e.InputError, 'engine identity'):
            self.replay(altered, self.repin(altered))

    def test_missing_case_and_family_drift(self):
        b = self.receipt['body']
        raw = e.unblob(b['results_b64'])
        variants = [raw[:raw.rfind(b'truncated')], raw.replace(b'synthetic-fast-v1', b'other'), raw + b'extra,0,1,1\n']
        for rows in variants:
            with self.subTest(rows=rows), self.assertRaises(e.InputError):
                e.make(e.unblob(b['pack_b64']), rows, self.seal)

    def test_raw_vs_normalized_bytes(self):
        b = self.receipt['body']
        raw = e.unblob(b['results_b64'])
        lines = raw.decode().splitlines()
        reordered = ('\r\n'.join([lines[0]] + list(reversed(lines[1:]))) + '\r\n').encode()
        other = e.make(e.unblob(b['pack_b64']), reordered, self.seal)
        self.assertNotEqual(other['body']['results_bytes_sha256'], b['results_bytes_sha256'])
        self.assertEqual(other['body']['analysis'], b['analysis'])

    def test_strict_json_and_shape(self):
        for raw in [b'{"body":{},"body":{}}', b'{"body":NaN}', b'[]', b'null', b'{}']:
            with self.subTest(raw=raw), self.assertRaises(e.InputError):
                e.replay(raw, self.seal, self.pin)
        altered = copy.deepcopy(self.receipt)
        altered['body']['extra'] = 1
        with self.assertRaises(e.InputError):
            self.replay(altered, self.repin(altered))

    def test_blob_and_size_bounds(self):
        for text in ['!', 'YR==', 1]:
            with self.subTest(text=text), self.assertRaises(e.InputError):
                e.unblob(text)
        with patch.object(e, 'MAX_RECEIPT', 10):
            with self.assertRaises(e.InputError):
                self.replay(self.receipt)
            with self.assertRaises(e.InputError):
                e.demo_receipt()

    def test_markdown_inert_labels_and_bidi(self):
        dangerous = '<img src=x onerror=alert(1)>|[go](https://x)`*\u202e'
        rendered = e.literal(dangerous)
        for forbidden in ['<', '>', '|', '[', ']', '`', '*', '\u202e']:
            self.assertNotIn(forbidden, rendered)
        self.assertIn('&#92;u202e', rendered)
        body = copy.deepcopy(self.receipt)
        body['body']['analysis']['candidates'][0]['name'] = dangerous
        text = e.markdown(body)
        self.assertNotIn('<img', text)
        self.assertIn('equivalence not established', text)
        self.assertIn('synthetic_demonstration', text)

    def test_direction_is_not_automatic_improvement(self):
        item = self.receipt['body']['analysis']['candidates'][0]
        item['familywise_reject_equal_discordance'] = True
        item['observed_direction'] = 'baseline'
        self.assertIn('Evidence favors baseline', e.markdown(self.receipt))
        self.assertNotIn('Evidence favors candidate', e.markdown(self.receipt))

    def test_source_snapshots_match_ancestors(self):
        pairs = [('seal_engine.py', 'benchmark-seal/benchmark_seal.py'),
                 ('frozen_engine.py', 'benchmark-seal/frozen_engine.py'),
                 ('ladder_engine.py', 'candidate-ladder/candidate_ladder.py')]
        for new, previous in pairs:
            self.assertEqual((HERE/new).read_bytes(), (HERE.parent/previous).read_bytes())

    def test_cli_standalone_replay_and_invalid_stdout(self):
        SCRATCH.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as directory:
            temp = Path(directory)
            tool = temp/'tool'
            tool.mkdir()
            for name in e.ENGINE_FILES:
                shutil.copyfile(HERE/name, tool/name)
            script = str(tool/'evidence_receipt.py')
            run = lambda *args: subprocess.run([sys.executable, '-B', script, *args], cwd=temp, capture_output=True)
            demo = run('demo', '--json')
            self.assertEqual(demo.returncode, 0, demo.stderr)
            receipt = json.loads(demo.stdout)
            (temp/'receipt.json').write_bytes(demo.stdout)
            options = ['replay', '--receipt', 'receipt.json', '--expected-seal-sha256', self.seal,
                       '--expected-receipt-sha256', receipt['receipt_sha256']]
            result = run(*options)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'replayed')
            md = run(*options, '--markdown')
            self.assertEqual(md.returncode, 0, md.stderr)
            self.assertIn(b'Benchmark evidence receipt', md.stdout)
            bad = run(*options[:-1], '0'*64)
            self.assertEqual(bad.returncode, 2)
            self.assertEqual(bad.stdout, b'')
            # Outside-workspace input rejected even if the file exists.
            outside = run('replay', '--receipt', str(HERE/'README.md'),
                          '--expected-seal-sha256', self.seal, '--expected-receipt-sha256', self.pin)
            self.assertEqual(outside.returncode, 2)
            self.assertEqual(outside.stdout, b'')

    def test_inputs_unchanged(self):
        pack = e.unblob(self.receipt['body']['pack_b64'])
        results = e.unblob(self.receipt['body']['results_b64'])
        before = (bytes(pack), bytes(results))
        e.make(pack, results, self.seal)
        self.assertEqual(before, (pack, results))


if __name__ == '__main__':
    unittest.main()
