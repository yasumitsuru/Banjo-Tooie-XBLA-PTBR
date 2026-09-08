#!/usr/bin/env python3
"""Regression tests for tools/extract_strings.py.

Tests run against a synthetic minimal .dat in a temp directory, then
exercise the real CLI.  No proprietary fixtures.

Historical RED evidence (Windows byte-stability bug):
  The original extractor emitted `source` with backslashes on Windows
  and used CRLF in strings.json (default text mode).  Both issues are
  now fixed (see extract_strings.py).  These tests verify the fixed
  behaviour; they are no longer expected to fail.
"""
import json
import os
import struct
import subprocess
import sys
import tempfile
import unittest

# Add project root to path for module imports
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_dat(n_strings: int = 3):
    """Build a minimal valid X360_strings.dat in memory.

    Layout:
      0x00  u32 magic = 0x000605F1
      0x04  6 x u32 (dummy header values)
      0x1C  N x u32 lengths (including null terminator)
      0x8EB4  pool of null-terminated strings

    Returns (dat_bytes, expected_lengths, pool_bytes).
    """
    magic = 0x000605F1
    header = struct.pack("<6I", 0, 0, 0, 0, 0, 0)
    # Deterministic nonempty strings: "S000", "S001", ... (%%03d)
    strings = [b"S%03d" % i for i in range(n_strings)]
    lengths = [len(s) + 1 for s in strings]  # +1 for null terminator
    length_table = struct.pack("<{}I".format(len(lengths)), *lengths)
    pool = b"".join(s + b"\x00" for s in strings)
    # Pad to POOL_OFF (0x8EB4) with zeros
    pool_off = 0x8EB4
    gap = pool_off - (4 + 24 + 4 * len(lengths))
    if gap < 0:
        raise ValueError("too many strings for minimal layout")
    gap_bytes = b"\x00" * gap
    dat = magic.to_bytes(4, "little") + header + length_table + gap_bytes + pool
    return dat, lengths, pool


class TestExtractSemantics(unittest.TestCase):
    """Test extraction logic against synthetic data."""

    def test_magic_validation(self):
        """Wrong magic raises ValueError."""
        from tools.extract_strings import extract
        bad = b"\x00" * 4 + b"\x00" * 24 + b"\x00" * 4 + b"\x00" * 10
        with self.assertRaises(ValueError):
            extract(bad)

    def test_count_matches_strings(self):
        """extract() returns count == number of strings."""
        from tools.extract_strings import extract
        dat, _, _ = _make_dat(3)
        magic, n, pool_end = extract(dat)
        self.assertEqual(n, 3)

    def test_count_one_string(self):
        """extract() works with a single string."""
        from tools.extract_strings import extract
        dat, _, _ = _make_dat(1)
        magic, n, pool_end = extract(dat)
        self.assertEqual(n, 1)

    def test_pool_end_exact(self):
        """pool_end == POOL_OFF + len(pool_bytes)."""
        from tools.extract_strings import extract
        dat, _, pool = _make_dat(3)
        magic, n, pool_end = extract(dat)
        self.assertEqual(pool_end, 0x8EB4 + len(pool))


class TestCrossPlatformByteStability(unittest.TestCase):
    """Verify cross-platform byte-stability of CLI output.

    Historical RED evidence (Windows byte-stability bug):
      The original extractor emitted `source` with backslashes on Windows
      and used CRLF in strings.json (default text mode).  Both issues are
      now fixed (see extract_strings.py).  These tests verify the fixed
      behaviour; they are no longer expected to fail.
    """

    def test_source_path_uses_forward_slashes(self):
        """source metadata must use forward slashes (/) regardless of OS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dat_path = os.path.join(tmpdir, "test.dat")
            dat, _, _ = _make_dat(3)
            with open(dat_path, "wb") as f:
                f.write(dat)
            result = subprocess.run(
                [sys.executable,
                 os.path.join(_PROJECT_ROOT, "tools", "extract_strings.py"),
                 "--dat", dat_path,
                 "--out", tmpdir],
                capture_output=True, text=True,
                cwd=_PROJECT_ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            out_json = os.path.join(tmpdir, "strings.json")
            with open(out_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            source = data["source"]
            # Must NOT contain backslashes
            self.assertNotIn("\\", source,
                             "source path uses backslashes: %r" % source)
            # Must contain forward slashes (path separator)
            self.assertIn("/", source,
                          "source path has no forward slashes: %r" % source)

    def test_strings_json_lf_only(self):
        """strings.json must use LF-only line endings on all platforms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dat_path = os.path.join(tmpdir, "test.dat")
            dat, _, _ = _make_dat(3)
            with open(dat_path, "wb") as f:
                f.write(dat)
            result = subprocess.run(
                [sys.executable,
                 os.path.join(_PROJECT_ROOT, "tools", "extract_strings.py"),
                 "--dat", dat_path,
                 "--out", tmpdir],
                capture_output=True, text=True,
                cwd=_PROJECT_ROOT,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            out_json = os.path.join(tmpdir, "strings.json")
            with open(out_json, "rb") as f:
                raw = f.read()
            # Must NOT contain CRLF
            self.assertNotIn(b"\r\n", raw,
                             "strings.json contains CRLF line endings")
            # Must contain LF
            self.assertIn(b"\n", raw,
                          "strings.json has no LF line endings")


class TestFilterOutput(unittest.TestCase):
    """Test filter_translatable.py output via CLI against synthetic extractor output."""

    def test_filter_cli_output(self):
        """filter must run via CLI with explicit --input/--out, produce strict UTF-8 JSON with required fields."""
        with tempfile.TemporaryDirectory() as tmpdir:
            dat_path = os.path.join(tmpdir, "test.dat")
            dat, expected_lengths, pool = _make_dat(3)
            with open(dat_path, "wb") as f:
                f.write(dat)
            # Step 1: extract
            r1 = subprocess.run(
                [sys.executable,
                 os.path.join(_PROJECT_ROOT, "tools", "extract_strings.py"),
                 "--dat", dat_path, "--out", tmpdir],
                capture_output=True, text=True,
                cwd=_PROJECT_ROOT,
            )
            self.assertEqual(r1.returncode, 0, r1.stderr)
            # Step 2: run filter via CLI with explicit --input/--out
            out_json = os.path.join(tmpdir, "source.json")
            r2 = subprocess.run(
                [sys.executable,
                 os.path.join(_PROJECT_ROOT, "tools", "filter_translatable.py"),
                 "--input", os.path.join(tmpdir, "strings.json"),
                 "--out", out_json],
                capture_output=True, text=True,
                cwd=_PROJECT_ROOT,
            )
            # Assert return code
            self.assertEqual(r2.returncode, 0, r2.stderr)
            # Assert strict UTF-8 JSON load
            with open(out_json, "rb") as f:
                raw = f.read()
            raw.decode("utf-8")  # strict UTF-8
            with open(out_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            # Assert top-level keys
            self.assertEqual(data["total_input"], 3)
            self.assertEqual(data["translatable"], 3)
            self.assertEqual(data["binary"], 0)
            self.assertIn("strings", data)
            # Assert len(strings) == 3
            self.assertEqual(len(data["strings"]), 3)
            # Assert required entry fields
            required = {"index", "offset", "byte_length", "encoding", "text"}
            for entry in data["strings"]:
                self.assertTrue(required.issubset(set(entry.keys())),
                                "missing fields: %s" % (required - set(entry.keys())))
            # Assert byte_length matches expected
            for i, entry in enumerate(data["strings"]):
                self.assertEqual(entry["byte_length"], expected_lengths[i])


# ---------------------------------------------------------------------------
# Tests for 0x80..0x8F placeholder range and 0x92 cp1252 fix (Task 1)
# ---------------------------------------------------------------------------

class TestDecodeSingleBytePlaceholderRange(unittest.TestCase):
    """Verify decode_single_byte handles 0x80..0x8F as placeholders and 0x92 as cp1252."""

    def test_0x80_becomes_placeholder(self):
        """Byte 0x80 must decode to [0x80] placeholder."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"\x80")
        self.assertEqual(result, "[0x80]")

    def test_0x8F_becomes_placeholder(self):
        """Byte 0x8F must decode to [0x8F] placeholder."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"\x8F")
        self.assertEqual(result, "[0x8F]")

    def test_0x92_becomes_U2019(self):
        """Byte 0x92 must decode to U+2019 (RIGHT SINGLE QUOTATION MARK), NOT [0x92]."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"\x92")
        self.assertEqual(result, "\u2019",
                         f"0x92 should be U+2019, got {result!r} (len={len(result)})")
        self.assertNotEqual(result, "[0x92]")

    def test_0x90_becomes_UFFFD(self):
        """Byte 0x90 is undefined in cp1252 → U+FFFD via errors='replace'."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"\x90")
        self.assertEqual(result, "\ufffd")

    def test_0x93_becomes_cp1252(self):
        """Byte 0x93 (cp1252 LEFT DOUBLE QUOTATION MARK U+201C) must decode correctly."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"\x93")
        self.assertEqual(result, "\u201C",
                         f"0x93 should be U+201C, got {result!r}")

    def test_0x94_becomes_cp1252(self):
        """Byte 0x94 (cp1252 RIGHT DOUBLE QUOTATION MARK U+201D) must decode correctly."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"\x94")
        self.assertEqual(result, "\u201D",
                         f"0x94 should be U+201D, got {result!r}")

    def test_0x9F_becomes_U0178(self):
        """Byte 0x9F is DEFINED in cp1252 as U+0178 (Ÿ), NOT undefined."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"\x9F")
        self.assertEqual(result, "\u0178",
                         f"0x9F should be U+0178 (Ÿ), got {result!r}")

    def test_0xA0_to_0xFF_use_cp1252(self):
        """Bytes 0xA0-0xFF must decode via cp1252."""
        from tools.extract_strings import decode_single_byte
        # 0xA0 = non-breaking space in cp1252
        self.assertEqual(decode_single_byte(b"\xA0"), "\u00A0")
        # 0xE1 = á in cp1252
        self.assertEqual(decode_single_byte(b"\xE1"), "\u00E1")
        # 0xE7 = ç in cp1252
        self.assertEqual(decode_single_byte(b"\xE7"), "\u00E7")

    def test_0x91_to_0x9F_table(self):
        """All defined bytes 0x91-0x9F must decode to their correct cp1252 codepoints."""
        from tools.extract_strings import decode_single_byte
        # 0x90 and 0x9D are undefined in cp1252 → U+FFFD
        self.assertEqual(decode_single_byte(b"\x90"), "\ufffd")
        self.assertEqual(decode_single_byte(b"\x9D"), "\ufffd")
        # Defined mappings (verified against Python cp1252 codec)
        table = {
            0x91: "\u2018",  # ' (U+2018 LEFT SINGLE QUOTATION MARK)
            0x92: "\u2019",  # ' (U+2019 RIGHT SINGLE QUOTATION MARK)
            0x93: "\u201C",  # " (U+201C LEFT DOUBLE QUOTATION MARK)
            0x94: "\u201D",  # " (U+201D RIGHT DOUBLE QUOTATION MARK)
            0x95: "\u2022",  # • (U+2022 BULLET)
            0x96: "\u2013",  # – (U+2013 EN DASH)
            0x97: "\u2014",  # — (U+2014 EM DASH)
            0x98: "\u02DC",  # ˜ (U+02DC SMALL TILDE)
            0x99: "\u2122",  # ™ (U+2122 TRADE MARK SIGN)
            0x9A: "\u0161",  # š (U+0161 SMALL LETTER S WITH STROKE)
            0x9B: "\u203A",  # › (U+203A SINGLE RIGHT-POINTING ANGLE QUOTATION MARK)
            0x9C: "\u0153",  # œ (U+0153 SMALL LIGATURE OE)
            0x9E: "\u017E",  # ž (U+017E SMALL LETTER Z WITH TILDE)
            0x9F: "\u0178",  # Ÿ (U+0178 LATIN CAPITAL LETTER Y WITH DIAERESIS)
        }
        for byte, expected_cp in table.items():
            result = decode_single_byte(bytes([byte]))
            self.assertEqual(result, expected_cp,
                             f"0x{byte:02X} should be U+{ord(expected_cp):04X}, got {result!r}")

    def test_undefined_cp1252_bytes_classified_as_binary(self):
        """decode_single_byte(0x90) and decode_single_byte(0x9D) both produce U+FFFD, which classify() rejects as binary."""
        from tools.extract_strings import decode_single_byte
        from tools.filter_translatable import classify
        # Both 0x90 and 0x9D are undefined in cp1252 → U+FFFD
        for byte in (0x90, 0x9D):
            decoded = decode_single_byte(bytes([byte]))
            self.assertEqual(decoded, "\ufffd",
                             f"decode_single_byte(0x{byte:02X}) should be U+FFFD, got {decoded!r}")
            entry = {
                "index": 100,
                "text": decoded,
                "encoding": "cp1252",
            }
            self.assertEqual(classify(entry), "binary",
                             f"classify({decoded!r}) should be binary")

    def test_cp1252_U2019_passes_filter(self):
        """A cp1252 entry containing U+2019 must pass the filter (it is valid cp1252)."""
        from tools.filter_translatable import classify
        entry = {
            "index": 100,
            "text": "BANJO\u2019S PACK",  # BANJO'S PACK with U+2019
            "encoding": "cp1252",
        }
        self.assertEqual(classify(entry), "translatable")

    def test_mixed_placeholder_and_U2019(self):
        """String with both [0x80] placeholder and U+2019 must decode correctly."""
        from tools.extract_strings import decode_single_byte
        raw = b"BANJO\x92S [\x80]"
        result = decode_single_byte(raw)
        self.assertIn("\u2019", result)
        self.assertIn("[0x80]", result)
        self.assertNotIn("[0x92]", result)


class TestDecodeSingleByteNullTerminator(unittest.TestCase):
    """Verify null terminator handling in decode_single_byte."""

    def test_null_terminator_stops_decode(self):
        """Bytes after null terminator must be ignored."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"HELLO\x00WORLD")
        self.assertEqual(result, "HELLO")

    def test_empty_string(self):
        """Single null byte produces empty string."""
        from tools.extract_strings import decode_single_byte
        result = decode_single_byte(b"\x00")
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main(verbosity=2)
