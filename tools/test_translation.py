#!/usr/bin/env python3
"""Tests for tools/init_translation.py.

Tests use small synthetic temp source/TM fixtures (no proprietary data).
Each test proves genuine RED first, then GREEN.

Testable functions exposed:
    load_json, build_tm_lookup, init_translation, write_output
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tools.init_translation import (
    build_tm_lookup,
    init_translation,
    load_json,
    write_output,
)

# ---------------------------------------------------------------------------
# Synthetic helpers
# ---------------------------------------------------------------------------

def _synthetic_source(en_count=5, non_en_start=1521, non_en_count=3):
    """Build a minimal source.json dict for testing.

    EN entries: indices 0..en_count-1 (all < 1521).
    Non-EN entries: indices non_en_start .. non_en_start+non_en_count-1.
    """
    strings = []
    for i in range(en_count):
        strings.append({
            "index": i,
            "offset": 0x8EB4 + i * 10,
            "byte_length": 10,
            "encoding": "cp1252",
            "text": f"EN_STRING_{i}",
        })
    for j in range(non_en_count):
        idx = non_en_start + j
        strings.append({
            "index": idx,
            "offset": 0x8EB4 + (en_count + j) * 10,
            "byte_length": 10,
            "encoding": "cp1252",
            "text": f"NONEN_STRING_{j}",
        })
    return {
        "source": "game/test/X360_strings.dat",
        "filter": "tools/filter_translatable.py",
        "criterion": "test criterion",
        "total_input": en_count + non_en_count,
        "translatable": en_count + non_en_count,
        "binary": 0,
        "strings": strings,
    }


def _synthetic_tm(approved_pairs=None, proposed_pairs=None, stale_indices=None):
    """Build a minimal tm.json dict.

    approved_pairs: list of (source_index, source_text, translation_text)
    proposed_pairs: list of (source_index, source_text, translation_text)
    stale_indices: list of source_index values that exist in TM but not in source
    """
    entries = []
    if approved_pairs:
        for idx, src, trans in approved_pairs:
            entries.append({
                "source": src,
                "translation": trans,
                "status": "approved",
                "source_index": idx,
                "notes": "test approved",
            })
    if proposed_pairs:
        for idx, src, trans in proposed_pairs:
            entries.append({
                "source": src,
                "translation": trans,
                "status": "proposed",
                "source_index": idx,
                "notes": "test proposed",
            })
    if stale_indices:
        for idx in stale_indices:
            entries.append({
                "source": f"STALE_{idx}",
                "translation": "STALE_TRANS",
                "status": "approved",
                "source_index": idx,
                "notes": "test stale",
            })
    return {
        "format": "tm-v1",
        "language_pair": "en-US -> pt-BR",
        "description": "test tm",
        "entries": entries,
    }


# ---------------------------------------------------------------------------
# Tests: load_json
# ---------------------------------------------------------------------------

class TestLoadJson(unittest.TestCase):
    """Test load_json reads strict UTF-8 JSON."""

    def test_load_valid_json(self):
        """RED: invalid UTF-8 should raise."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            f.write(b"\xff\xfe")  # invalid UTF-8
            tmp = f.name
        try:
            with self.assertRaises(UnicodeDecodeError):
                load_json(tmp)
        finally:
            os.unlink(tmp)

    def test_load_valid_utf8(self):
        """GREEN: valid UTF-8 JSON loads correctly."""
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w", encoding="utf-8") as f:
            json.dump({"key": "value"}, f)
            tmp = f.name
        try:
            data = load_json(tmp)
            self.assertEqual(data, {"key": "value"})
        finally:
            os.unlink(tmp)


# ---------------------------------------------------------------------------
# Tests: build_tm_lookup
# ---------------------------------------------------------------------------

class TestBuildTmLookup(unittest.TestCase):
    """Test TM lookup construction and duplicate detection."""

    def test_approved_only_in_lookup(self):
        """RED: proposed entries should NOT be in lookup."""
        tm = _synthetic_tm(
            approved_pairs=[(0, "EN_STRING_0", "PT_STRING_0")],
            proposed_pairs=[(1, "EN_STRING_1", "PT_STRING_1")],
        )
        lookup = build_tm_lookup(tm)
        self.assertIn(0, lookup)
        self.assertNotIn(1, lookup)

    def test_duplicate_approved_raises(self):
        """RED: duplicate approved source_index should raise ValueError."""
        tm = _synthetic_tm(
            approved_pairs=[
                (0, "EN_STRING_0", "PT_A"),
                (0, "EN_STRING_0", "PT_B"),
            ],
        )
        with self.assertRaises(ValueError) as ctx:
            build_tm_lookup(tm)
        self.assertIn("duplicate approved source_index 0", str(ctx.exception))

    def test_empty_tm_returns_empty(self):
        """GREEN: empty tm.json returns empty lookup."""
        tm = _synthetic_tm()
        lookup = build_tm_lookup(tm)
        self.assertEqual(lookup, {})

    def test_missing_source_index_raises(self):
        """RED: approved entry without source_index accepted. GREEN: raises ValueError."""
        tm = {"format": "tm-v1", "entries": [
            {"source": "X", "translation": "Y", "status": "approved"},
        ]}
        with self.assertRaises(ValueError) as ctx:
            build_tm_lookup(tm)
        self.assertIn("missing source_index", str(ctx.exception).lower())

    def test_missing_source_field_raises(self):
        """RED: approved entry without source field accepted. GREEN: raises ValueError."""
        tm = {"format": "tm-v1", "entries": [
            {"translation": "Y", "status": "approved", "source_index": 0},
        ]}
        with self.assertRaises(ValueError) as ctx:
            build_tm_lookup(tm)
        self.assertIn("missing source", str(ctx.exception).lower())

    def test_missing_translation_field_raises(self):
        """RED: approved entry without translation field accepted. GREEN: raises ValueError."""
        tm = {"format": "tm-v1", "entries": [
            {"source": "X", "status": "approved", "source_index": 0},
        ]}
        with self.assertRaises(ValueError) as ctx:
            build_tm_lookup(tm)
        self.assertIn("missing translation", str(ctx.exception).lower())

    def test_empty_translation_raises(self):
        """RED: approved entry with empty translation accepted. GREEN: raises ValueError."""
        tm = {"format": "tm-v1", "entries": [
            {"source": "X", "translation": "", "status": "approved", "source_index": 0},
        ]}
        with self.assertRaises(ValueError) as ctx:
            build_tm_lookup(tm)
        self.assertIn("empty translation", str(ctx.exception).lower())

    def test_proposed_malformed_ignored(self):
        """RED: malformed proposed entry causes error. GREEN: proposed ignored even malformed."""
        tm = {"format": "tm-v1", "entries": [
            {"source": "X", "status": "proposed"},  # missing translation, source_index
        ]}
        lookup = build_tm_lookup(tm)  # should not raise
        self.assertEqual(lookup, {})

    def test_missing_entries_key_raises(self):
        """RED: tm_data without 'entries' accepted. GREEN: raises ValueError."""
        tm = {"format": "tm-v1"}  # no 'entries' key
        with self.assertRaises(ValueError) as ctx:
            build_tm_lookup(tm)
        self.assertIn("entries", str(ctx.exception).lower())

    def test_non_list_entries_raises(self):
        """RED: tm_data['entries'] as non-list accepted. GREEN: raises ValueError."""
        tm = {"format": "tm-v1", "entries": "not a list"}
        with self.assertRaises(ValueError) as ctx:
            build_tm_lookup(tm)
        self.assertIn("entries", str(ctx.exception).lower())
        self.assertIn("list", str(ctx.exception).lower())


# ---------------------------------------------------------------------------
# Tests: init_translation (core logic)
# ---------------------------------------------------------------------------

class TestInitTranslation(unittest.TestCase):
    """Test init_translation core logic."""

    def test_all_records_preserved(self):
        """RED: without init, records would be missing. GREEN: all source records preserved."""
        source = _synthetic_source(en_count=3, non_en_count=2)
        tm = _synthetic_tm(approved_pairs=[])
        result = init_translation(source, build_tm_lookup(tm))
        self.assertEqual(len(result["strings"]), len(source["strings"]))
        for i, (orig, out) in enumerate(zip(source["strings"], result["strings"])):
            self.assertEqual(out["index"], orig["index"])
            self.assertEqual(out["offset"], orig["offset"])
            self.assertEqual(out["byte_length"], orig["byte_length"])
            self.assertEqual(out["encoding"], orig["encoding"])
            self.assertEqual(out["text"], orig["text"])

    def test_metadata_preserved(self):
        """RED: metadata would be lost. GREEN: all top-level keys preserved."""
        source = _synthetic_source(en_count=2, non_en_count=1)
        tm = _synthetic_tm(approved_pairs=[])
        result = init_translation(source, build_tm_lookup(tm))
        for key in ("source", "filter", "criterion", "total_input", "translatable", "binary"):
            self.assertIn(key, result)
            self.assertEqual(result[key], source[key])

    def test_order_preserved(self):
        """RED: order would be scrambled. GREEN: string order matches source."""
        source = _synthetic_source(en_count=5, non_en_count=3)
        tm = _synthetic_tm(approved_pairs=[])
        result = init_translation(source, build_tm_lookup(tm))
        for i, orig in enumerate(source["strings"]):
            self.assertEqual(result["strings"][i]["index"], orig["index"])

    def test_translation_key_everywhere(self):
        """RED: translation key missing. GREEN: every entry has 'translation'."""
        source = _synthetic_source(en_count=2, non_en_count=1)
        tm = _synthetic_tm(approved_pairs=[])
        result = init_translation(source, build_tm_lookup(tm))
        for entry in result["strings"]:
            self.assertIn("translation", entry)

    def test_only_approved_in_range_seeded(self):
        """RED: nothing seeded. GREEN: only approved EN entries get translation."""
        source = _synthetic_source(en_count=5, non_en_count=2)
        tm = _synthetic_tm(
            approved_pairs=[
                (0, "EN_STRING_0", "PT_ZERO"),
                (2, "EN_STRING_2", "PT_TWO"),
            ],
            proposed_pairs=[
                (1, "EN_STRING_1", "PT_ONE_PROPOSED"),
            ],
        )
        result = init_translation(source, build_tm_lookup(tm))
        # Approved EN entries seeded
        self.assertEqual(result["strings"][0]["translation"], "PT_ZERO")
        self.assertEqual(result["strings"][2]["translation"], "PT_TWO")
        # Proposed NOT seeded (null)
        self.assertIsNone(result["strings"][1]["translation"])
        # Non-EN null
        self.assertIsNone(result["strings"][5]["translation"])
        self.assertIsNone(result["strings"][6]["translation"])

    def test_proposed_entries_null(self):
        """RED: proposed would be seeded. GREEN: proposed stays null."""
        source = _synthetic_source(en_count=3, non_en_count=1)
        tm = _synthetic_tm(
            approved_pairs=[],
            proposed_pairs=[(1, "EN_STRING_1", "PT_ONE")],
        )
        result = init_translation(source, build_tm_lookup(tm))
        self.assertIsNone(result["strings"][1]["translation"])

    def test_non_en_entries_null(self):
        """RED: non-EN would be populated. GREEN: non-EN stays null."""
        source = _synthetic_source(en_count=2, non_en_count=3)
        tm = _synthetic_tm(
            approved_pairs=[
                (1521, "NONEN_STRING_0", "PT_NONEN"),
            ],
        )
        result = init_translation(source, build_tm_lookup(tm))
        for i in range(2, 5):
            self.assertIsNone(result["strings"][i]["translation"])

    def test_stale_approved_raises(self):
        """RED: stale approved index accepted. GREEN: stale raises ValueError."""
        source = _synthetic_source(en_count=3, non_en_count=1)
        # TM has approved entry for index 0 but with wrong source text
        tm = _synthetic_tm(
            approved_pairs=[(0, "WRONG_TEXT", "PT_ZERO")],
        )
        with self.assertRaises(ValueError) as ctx:
            init_translation(source, build_tm_lookup(tm))
        self.assertIn("stale", str(ctx.exception).lower())

    def test_missing_approved_index_raises(self):
        """RED: missing approved index accepted. GREEN: missing raises ValueError."""
        source = _synthetic_source(en_count=2, non_en_count=1)
        # TM has approved entry for index 999 which doesn't exist in source
        tm = _synthetic_tm(
            approved_pairs=[(999, "SOME_TEXT", "PT_SOME")],
        )
        with self.assertRaises(ValueError) as ctx:
            init_translation(source, build_tm_lookup(tm))
        self.assertIn("missing approved index", str(ctx.exception))

    def test_duplicate_approved_raises(self):
        """RED: duplicate approved accepted. GREEN: duplicate raises ValueError."""
        source = _synthetic_source(en_count=3, non_en_count=1)
        tm = _synthetic_tm(
            approved_pairs=[
                (0, "EN_STRING_0", "PT_A"),
                (0, "EN_STRING_0", "PT_B"),
            ],
        )
        with self.assertRaises(ValueError):
            init_translation(source, build_tm_lookup(tm))

    def test_no_meta_in_output(self):
        """RED: _meta would be persisted. GREEN: output top-level keys exactly match source keys."""
        source = _synthetic_source(en_count=3, non_en_count=2)
        tm = _synthetic_tm(approved_pairs=[])
        result = init_translation(source, build_tm_lookup(tm))
        # No _meta key
        self.assertNotIn("_meta", result)
        # Top-level keys exactly match source (minus _meta)
        source_keys = set(source.keys())
        result_keys = set(result.keys())
        self.assertEqual(result_keys, source_keys)

    def test_extra_field_survives(self):
        """RED: extra per-entry fields lost. GREEN: dict(entry) preserves them."""
        source = _synthetic_source(en_count=2, non_en_count=1)
        # Add custom field to first entry
        source["strings"][0]["custom_field"] = "custom_value"
        tm = _synthetic_tm(approved_pairs=[])
        result = init_translation(source, build_tm_lookup(tm))
        self.assertEqual(result["strings"][0]["custom_field"], "custom_value")
        # translation key also present
        self.assertIn("translation", result["strings"][0])

    def test_missing_strings_key_raises(self):
        """RED: source_data without 'strings' accepted. GREEN: raises ValueError."""
        source = {"source": "game/test/X360_strings.dat"}  # no 'strings'
        tm = _synthetic_tm(approved_pairs=[])
        with self.assertRaises(ValueError) as ctx:
            init_translation(source, build_tm_lookup(tm))
        self.assertIn("strings", str(ctx.exception).lower())

    def test_non_list_strings_raises(self):
        """RED: source_data['strings'] as non-list accepted. GREEN: raises ValueError."""
        source = {"source": "game/test/X360_strings.dat", "strings": "not a list"}
        tm = _synthetic_tm(approved_pairs=[])
        with self.assertRaises(ValueError) as ctx:
            init_translation(source, build_tm_lookup(tm))
        self.assertIn("strings", str(ctx.exception).lower())
        self.assertIn("list", str(ctx.exception).lower())

    def test_key_order_preserved_strings_not_last(self):
        """RED: key order scrambled (strings forced last). GREEN: dict() preserves order."""
        # Build source where 'strings' is NOT the last key
        source = {
            "source": "game/test/X360_strings.dat",
            "filter": "tools/filter_translatable.py",
            "strings": [
                {"index": 0, "offset": 0, "byte_length": 5, "encoding": "cp1252", "text": "HELLO"},
            ],
            "total_input": 1,
            "translatable": 1,
            "binary": 0,
        }
        tm = _synthetic_tm(approved_pairs=[])
        result = init_translation(source, build_tm_lookup(tm))
        # Key order must match source exactly
        self.assertEqual(list(result.keys()), list(source.keys()))
        # 'strings' should be at index 2 (third position), not last
        self.assertEqual(list(result.keys()).index("strings"), 2)


# ---------------------------------------------------------------------------
# Tests: write_output
# ---------------------------------------------------------------------------

class TestWriteOutput(unittest.TestCase):
    """Test write_output file behavior."""

    def test_no_overwrite_without_force(self):
        """RED: existing output would be silently overwritten. GREEN: CLI refuses without --force."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "translated.json")
            # Create existing file
            with open(out_path, "w") as f:
                f.write('{"existing": true}')
            # Run CLI without --force
            r = subprocess.run(
                [sys.executable,
                 os.path.join(_PROJECT_ROOT, "tools", "init_translation.py"),
                 "--out", out_path],
                capture_output=True, text=True,
                cwd=_PROJECT_ROOT,
            )
            self.assertNotEqual(r.returncode, 0)
            self.assertIn("exists", r.stderr.lower())
            # File unchanged
            with open(out_path) as f:
                self.assertEqual(json.load(f), {"existing": True})

    def test_force_overwrites(self):
        """RED: force would not work. GREEN: --force overwrites."""
        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = os.path.join(tmpdir, "translated.json")
            with open(out_path, "w") as f:
                f.write('{"existing": true}')
            r = subprocess.run(
                [sys.executable,
                 os.path.join(_PROJECT_ROOT, "tools", "init_translation.py"),
                 "--out", out_path,
                 "--force"],
                capture_output=True, text=True,
                cwd=_PROJECT_ROOT,
            )
            self.assertEqual(r.returncode, 0)
            # File was overwritten
            with open(out_path) as f:
                data = json.load(f)
            self.assertIn("strings", data)

    def test_lf_only_line_endings(self):
        """RED: CRLF would be used on Windows. GREEN: LF-only output."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = _synthetic_source(en_count=2, non_en_count=1)
            tm = _synthetic_tm(approved_pairs=[])
            result = init_translation(source, build_tm_lookup(tm))
            out_path = os.path.join(tmpdir, "translated.json")
            write_output(result, out_path)
            with open(out_path, "rb") as f:
                raw = f.read()
            self.assertNotIn(b"\r\n", raw, "output contains CRLF")
            self.assertIn(b"\n", raw, "output has no LF")

    def test_deterministic_repeated_output(self):
        """RED: output would differ between runs. GREEN: identical SHA on repeat."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = _synthetic_source(en_count=5, non_en_count=3)
            tm = _synthetic_tm(
                approved_pairs=[
                    (0, "EN_STRING_0", "PT_ZERO"),
                    (3, "EN_STRING_3", "PT_THREE"),
                ],
            )
            result = init_translation(source, build_tm_lookup(tm))
            out1 = os.path.join(tmpdir, "out1.json")
            out2 = os.path.join(tmpdir, "out2.json")
            write_output(result, out1)
            write_output(result, out2)
            with open(out1, "rb") as f:
                h1 = __import__("hashlib").sha256(f.read()).hexdigest()
            with open(out2, "rb") as f:
                h2 = __import__("hashlib").sha256(f.read()).hexdigest()
            self.assertEqual(h1, h2, "output not deterministic")

    def test_deterministic_indent_1(self):
        """GREEN: output uses indent=1."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = _synthetic_source(en_count=1, non_en_count=0)
            tm = _synthetic_tm(approved_pairs=[])
            result = init_translation(source, build_tm_lookup(tm))
            out_path = os.path.join(tmpdir, "out.json")
            write_output(result, out_path)
            with open(out_path) as f:
                content = f.read()
            # indent=1 means " {\n" not "  {\n"
            self.assertIn('"strings": [\n', content)

    def test_bare_filename_no_dir_creation(self):
        """RED: bare filename crashes (dirname empty). GREEN: works with bare filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = _synthetic_source(en_count=1, non_en_count=0)
            tm = _synthetic_tm(approved_pairs=[])
            result = init_translation(source, build_tm_lookup(tm))
            # Change cwd to tempdir and use bare filename
            old_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                write_output(result, "translated.json")
            finally:
                os.chdir(old_cwd)
            # File should exist in tempdir
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "translated.json")))


# ---------------------------------------------------------------------------
# Tests: CLI integration
# ---------------------------------------------------------------------------

class TestCliIntegration(unittest.TestCase):
    """Real CLI tests (not only function-level)."""

    def test_cli_produces_valid_output(self):
        """RED: CLI would fail or produce invalid JSON. GREEN: valid translated.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write synthetic source
            source = _synthetic_source(en_count=3, non_en_count=2)
            source_path = os.path.join(tmpdir, "source.json")
            with open(source_path, "w", encoding="utf-8") as f:
                json.dump(source, f, ensure_ascii=False, indent=1)
            # Write synthetic TM
            tm = _synthetic_tm(
                approved_pairs=[
                    (0, "EN_STRING_0", "PT_ZERO"),
                    (1, "EN_STRING_1", "PT_ONE"),
                ],
                proposed_pairs=[(2, "EN_STRING_2", "PT_TWO")],
            )
            tm_path = os.path.join(tmpdir, "tm.json")
            with open(tm_path, "w", encoding="utf-8") as f:
                json.dump(tm, f, ensure_ascii=False, indent=1)
            out_path = os.path.join(tmpdir, "translated.json")
            r = subprocess.run(
                [sys.executable,
                 os.path.join(_PROJECT_ROOT, "tools", "init_translation.py"),
                 "--source", source_path,
                 "--tm", tm_path,
                 "--out", out_path,
                 "--force"],
                capture_output=True, text=True,
                cwd=_PROJECT_ROOT,
            )
            self.assertEqual(r.returncode, 0, f"CLI failed: {r.stderr}")
            # Verify output
            self.assertTrue(os.path.exists(out_path))
            with open(out_path, "rb") as f:
                f.read().decode("utf-8")  # strict UTF-8
            with open(out_path, encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(data["strings"][0]["translation"], "PT_ZERO")
            self.assertEqual(data["strings"][1]["translation"], "PT_ONE")
            self.assertIsNone(data["strings"][2]["translation"])
            self.assertIsNone(data["strings"][3]["translation"])
            self.assertIsNone(data["strings"][4]["translation"])

    def test_cli_prints_counts(self):
        """RED: CLI would not print counts. GREEN: concise counts printed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = _synthetic_source(en_count=3, non_en_count=2)
            source_path = os.path.join(tmpdir, "source.json")
            with open(source_path, "w", encoding="utf-8") as f:
                json.dump(source, f)
            tm = _synthetic_tm(approved_pairs=[])
            tm_path = os.path.join(tmpdir, "tm.json")
            with open(tm_path, "w", encoding="utf-8") as f:
                json.dump(tm, f)
            out_path = os.path.join(tmpdir, "translated.json")
            r = subprocess.run(
                [sys.executable,
                 os.path.join(_PROJECT_ROOT, "tools", "init_translation.py"),
                 "--source", source_path,
                 "--tm", tm_path,
                 "--out", out_path,
                 "--force"],
                capture_output=True, text=True,
                cwd=_PROJECT_ROOT,
            )
            self.assertEqual(r.returncode, 0)
            self.assertIn("total:", r.stdout)
            self.assertIn("EN:", r.stdout)
            self.assertIn("non-EN:", r.stdout)
            self.assertIn("approved seeded:", r.stdout)
            self.assertIn("EN null:", r.stdout)


# ---------------------------------------------------------------------------
# Tests: non-EN TM entries never applied
# ---------------------------------------------------------------------------

class TestNonEnTmNeverApplied(unittest.TestCase):
    """Verify non-EN TM entries (source_index >= 1521) are never applied."""

    def test_non_en_approved_not_applied(self):
        """RED: non-EN approved would be applied. GREEN: stays null."""
        source = _synthetic_source(en_count=2, non_en_count=3)
        # Use indices that exist in source (1521 and 1522 are non-EN entries)
        tm = _synthetic_tm(
            approved_pairs=[
                (1521, "NONEN_STRING_0", "PT_NONEN"),
            ],
        )
        result = init_translation(source, build_tm_lookup(tm))
        # Non-EN entries should have null translation
        for i in range(2, 5):
            self.assertIsNone(result["strings"][i]["translation"])

    def test_non_en_stale_text_raises(self):
        """RED: non-EN stale text accepted. GREEN: raises ValueError."""
        source = _synthetic_source(en_count=2, non_en_count=3)
        # TM has approved entry for index 1521 with wrong source text
        tm = _synthetic_tm(
            approved_pairs=[
                (1521, "WRONG_NONEN_TEXT", "PT_NONEN"),
            ],
        )
        with self.assertRaises(ValueError) as ctx:
            init_translation(source, build_tm_lookup(tm))
        self.assertIn("stale", str(ctx.exception).lower())


# ---------------------------------------------------------------------------
# Tests: exact source string match required
# ---------------------------------------------------------------------------

class TestExactSourceMatch(unittest.TestCase):
    """Verify TM source must exactly match source.text."""

    def test_mismatched_source_text_raises(self):
        """RED: mismatched source accepted. GREEN: raises ValueError."""
        source = _synthetic_source(en_count=3, non_en_count=1)
        tm = _synthetic_tm(
            approved_pairs=[(0, "WRONG_MATCH", "PT_ZERO")],
        )
        with self.assertRaises(ValueError) as ctx:
            init_translation(source, build_tm_lookup(tm))
        self.assertIn("stale", str(ctx.exception).lower())

    def test_exact_match_seeded(self):
        """RED: exact match not seeded. GREEN: exact match seeded."""
        source = _synthetic_source(en_count=3, non_en_count=1)
        tm = _synthetic_tm(
            approved_pairs=[(0, "EN_STRING_0", "PT_ZERO")],
        )
        result = init_translation(source, build_tm_lookup(tm))
        self.assertEqual(result["strings"][0]["translation"], "PT_ZERO")


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    unittest.main(verbosity=2)
