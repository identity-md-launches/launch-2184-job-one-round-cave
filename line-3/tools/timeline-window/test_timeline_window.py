"""Focused offline checks for verified half-open incident windows."""

import unittest

import replay
import timeline_window as window


class WindowTests(unittest.TestCase):
    def setUp(self):
        self.pack = replay.make_pack([
            ("front.log", b"2026-10-18T10:00:00Z begin\n2026-10-18T10:00:02Z accepted\nundated diagnostic\n"),
            ("back.log", b"2026-10-18T10:00:04Z done\n"),
        ], ignore_unmatched=True, clock_uncertainty_ms=250)

    def test_possible_overlap_and_explicit_omission(self):
        result = window.inspect(self.pack, "2026-10-18T10:00:02Z", "2026-10-18T10:00:04Z")
        self.assertEqual(result["counts"]["possible_overlap"], 2)
        self.assertEqual(result["counts"]["contained"], 0)
        self.assertEqual(result["counts"]["outside"], 1)
        self.assertEqual(result["counts"]["omitted_lines_total"], 1)
        self.assertEqual([item["event"]["source"] for item in result["events"]],
                         ["front.log", "back.log"])

    def test_half_open_endpoint_and_precision(self):
        pack = replay.make_pack([("x", b"2026-10-18T10:00:00Z first\n2026-10-18T10:00:01Z second\n")])
        result = window.inspect(pack, "2026-10-18T10:00:01Z", "2026-10-18T10:00:02Z")
        self.assertEqual(result["counts"]["matching"], 1)
        self.assertEqual(result["events"][0]["event"]["line"], 2)
        self.assertEqual(result["events"][0]["classification"], "contained")

    def test_limit_never_hides_totals(self):
        result = window.inspect(self.pack, "2026-10-18T10:00:02Z", "2026-10-18T10:00:04Z", 0)
        self.assertEqual(result["counts"]["matching"], 2)
        self.assertEqual(result["counts"]["not_shown"], 2)
        self.assertEqual(result["counts"]["omitted_lines_not_shown"], 1)
        self.assertEqual(result["events"], [])

    def test_tampered_pack_rejected_before_query(self):
        self.pack["timeline"]["events"][0]["message"] = "fabricated"
        with self.assertRaises(replay.ReplayError):
            window.inspect(self.pack, "2026-10-18T10:00:00Z", "2026-10-18T10:00:10Z")

    def test_bad_boundaries_and_limit(self):
        for start, end in [("2026-10-18T10:00:02Z", "2026-10-18T10:00:02Z"),
                           ("2026-10-18T10:00:02", "2026-10-18T10:00:04Z"),
                           ("2026-10-18T10:00:02+24:00", "2026-10-18T10:00:04Z")]:
            with self.subTest(start=start):
                with self.assertRaises(replay.ReplayError):
                    window.inspect(self.pack, start, end)
        with self.assertRaises(replay.ReplayError):
            window.inspect(self.pack, "2026-10-18T10:00:02Z", "2026-10-18T10:00:04Z", 201)

    def test_offset_boundaries_normalize(self):
        result = window.inspect(self.pack, "2026-10-18T12:00:02+02:00", "2026-10-18T12:00:04+02:00")
        self.assertEqual(result["query"]["start_utc_inclusive"], "2026-10-18T10:00:02Z")
        self.assertEqual(result["counts"]["matching"], 2)


if __name__ == "__main__":
    unittest.main()
