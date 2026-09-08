#!/usr/bin/env python3
"""Focused tests for tools/validate_translation.py."""
import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from tools.validate_translation import validate_translation


def _make_source(en_count=5, non_en_count=3):
    strings = []
    for i in range(en_count):
        t = f"EN_STRING_{i}"
        strings.append({"index": i, "offset": 0x8EB4 + i * 10, "byte_length": len(t), "encoding": "cp1252", "text": t})
    for j in range(non_en_count):
        idx = 1521 + j
        t = f"NONEN_STRING_{j}"
        strings.append({"index": idx, "offset": 0x8EB4 + (en_count + j) * 10, "byte_length": len(t), "encoding": "cp1252", "text": t})
    return {"source": "game/test/X360_strings.dat", "filter": "tools/filter_translatable.py", "criterion": "test criterion", "total_input": en_count + non_en_count, "translatable": en_count + non_en_count, "binary": 0, "strings": strings}


def _make_translated(strings_list):
    return {"source": "game/test/X360_strings.dat", "filter": "tools/filter_translatable.py", "criterion": "test criterion", "total_input": len(strings_list), "translatable": len(strings_list), "binary": 0, "strings": strings_list}


def _rec(index, text="HELLO", translation=None, encoding="cp1252", offset=None, byte_length=None):
    """Create a translated record that mirrors source metadata.

    When offset/byte_length are None, compute them from text to match
    what _make_source would produce for the same index.
    """
    if offset is None:
        offset = 0x8EB4 + index * 10
    if byte_length is None:
        byte_length = len(text)
    return {"index": index, "offset": offset, "byte_length": byte_length, "encoding": encoding, "text": text, "translation": translation}


class TestGate1Structure(unittest.TestCase):
    def test_source_not_dict(self):
        result = validate_translation("not a dict", _make_translated([]))
        self.assertTrue(any("not a JSON object" in e for e in result["errors"]))
    def test_translated_not_dict(self):
        result = validate_translation(_make_source(), "not a dict")
        self.assertTrue(any("not a JSON object" in e for e in result["errors"]))
    def test_source_missing_strings(self):
        result = validate_translation({"source": "x"}, _make_translated([]))
        self.assertTrue(any("missing 'strings'" in e for e in result["errors"]))
    def test_translated_missing_strings(self):
        result = validate_translation(_make_source(), {"source": "x"})
        self.assertTrue(any("missing 'strings'" in e for e in result["errors"]))
    def test_source_strings_not_list(self):
        src = _make_source(); src["strings"] = "not a list"
        result = validate_translation(src, _make_translated([]))
        self.assertTrue(any("not a list" in e for e in result["errors"]))
    def test_translated_strings_not_list(self):
        trans = _make_translated("not a list")
        result = validate_translation(_make_source(), trans)
        self.assertTrue(any("not a list" in e for e in result["errors"]))


class TestGate2Structural(unittest.TestCase):
    def test_extra_top_key_in_translated(self):
        src = _make_source(en_count=2, non_en_count=1); trans = _make_source(en_count=2, non_en_count=1); trans["extra_key"] = "x"
        result = validate_translation(src, trans)
        self.assertTrue(any("key mismatch" in e for e in result["errors"]))
    def test_missing_top_key_in_translated(self):
        src = _make_source(en_count=2, non_en_count=1); trans = _make_source(en_count=2, non_en_count=1); del trans["binary"]
        result = validate_translation(src, trans)
        self.assertTrue(any("key mismatch" in e for e in result["errors"]))
    def test_metadata_value_mutation(self):
        src = _make_source(en_count=2, non_en_count=1); trans = _make_source(en_count=2, non_en_count=1); trans["source"] = "game/modified/X360_strings.dat"
        result = validate_translation(src, trans)
        self.assertTrue(any("mismatch" in e for e in result["errors"]))
    def test_record_count_mismatch(self):
        src = _make_source(en_count=3, non_en_count=1); trans = _make_translated([_rec(0), _rec(1)])
        result = validate_translation(src, trans)
        self.assertTrue(any("count mismatch" in e for e in result["errors"]))
    def test_extra_records_in_translated(self):
        src = _make_source(en_count=2, non_en_count=1); trans = _make_translated([_rec(0), _rec(1), _rec(2), _rec(3)])
        result = validate_translation(src, trans)
        self.assertTrue(any("extra record" in e for e in result["errors"]))
    def test_source_field_offset_changed(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=None), _rec(1521, "NONEN_STRING_0")])
        trans["strings"][1]["offset"] = 99999
        result = validate_translation(src, trans)
        self.assertTrue(any("'offset' mismatch" in e for e in result["errors"]))
    def test_source_field_text_changed(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "MODIFIED_TEXT", translation=None), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans)
        self.assertTrue(any("'text' mismatch" in e for e in result["errors"]))
    def test_source_field_encoding_changed(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=None, encoding="utf-16-be"), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans)
        self.assertTrue(any("'encoding' mismatch" in e for e in result["errors"]))
    def test_source_field_byte_length_changed(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=None), _rec(1521, "NONEN_STRING_0")])
        trans["strings"][1]["byte_length"] = 999
        result = validate_translation(src, trans)
        self.assertTrue(any("'byte_length' mismatch" in e for e in result["errors"]))
    def test_source_field_index_changed(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(999, "EN_STRING_1", translation=None), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans)
        self.assertTrue(any("'index' mismatch" in e for e in result["errors"]))
    def test_missing_translation_field(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), {"index": 1, "offset": 0, "byte_length": 10, "encoding": "cp1252", "text": "EN_STRING_1"}, _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans)
        self.assertTrue(any("missing 'translation'" in e for e in result["errors"]))
    def test_extra_field_in_record_ok(self):
        src = _make_source(en_count=2, non_en_count=1)
        src["strings"][1]["custom"] = "value"
        trans = _make_translated([
            _rec(0, "EN_STRING_0"),
            {**_rec(1, "EN_STRING_1", translation=None), "custom": "value"},
            {**_rec(1521, "NONEN_STRING_0"), "offset": src["strings"][2]["offset"]},
        ])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])


class TestGate3Scope(unittest.TestCase):
    def test_non_en_non_null_translation(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=None), _rec(1521, "NONEN_STRING_0", translation="PT_TRANSLATION")])
        result = validate_translation(src, trans)
        self.assertTrue(any("non-EN entry has non-null" in e for e in result["errors"]))
    def test_non_en_null_ok(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([
            _rec(0, "EN_STRING_0"),
            _rec(1, "EN_STRING_1", translation=None),
            {**_rec(1521, "NONEN_STRING_0", translation=None), "offset": src["strings"][2]["offset"]},
        ])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_translated_only_extra_key_fails(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([
            _rec(0, "EN_STRING_0"),
            {**_rec(1, "EN_STRING_1", translation=None), "extra_only": "bad"},
            {**_rec(1521, "NONEN_STRING_0"), "offset": src["strings"][2]["offset"]},
        ])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("extra keys" in e for e in result["errors"]))
    def test_source_custom_omitted_fails(self):
        src = _make_source(en_count=2, non_en_count=1)
        src["strings"][1]["custom"] = "value"
        trans = _make_translated([
            _rec(0, "EN_STRING_0"),
            _rec(1, "EN_STRING_1", translation=None),
            {**_rec(1521, "NONEN_STRING_0"), "offset": src["strings"][2]["offset"]},
        ])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("omits source keys" in e for e in result["errors"]))
    def test_en_null_strict_fails(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=None), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans, allow_incomplete=False)
        self.assertTrue(any("null translation" in e for e in result["errors"]))
    def test_en_null_allow_incomplete_ok(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([
            _rec(0, "EN_STRING_0"),
            _rec(1, "EN_STRING_1", translation=None),
            {**_rec(1521, "NONEN_STRING_0"), "offset": src["strings"][2]["offset"]},
        ])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_en_empty_translation_fails(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=""), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("empty or whitespace" in e for e in result["errors"]))
    def test_en_whitespace_translation_fails(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation="   \t  \n  "), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("empty or whitespace" in e for e in result["errors"]))
    def test_en_non_string_translation_fails(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=123), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("not a string" in e for e in result["errors"]))


class TestGate4Content(unittest.TestCase):
    def test_ufffd_in_translation(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation="has \ufffd char"), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("U+FFFD" in e for e in result["errors"]))
    def test_cr_in_translation(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation="has \r CR"), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("carriage return" in e for e in result["errors"]))
    def test_placeholder_preserved(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "PRESS [0x80] OR [0x81]"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "PRESS [0x80] OR [0x81]", translation="PRESSIONA [0x80] OU [0x81]", byte_length=22)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_placeholder_reordered(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "[0x80] [0x81]"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "[0x80] [0x81]", translation="[0x81] [0x80]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("sequence mismatch" in e for e in result["errors"]))
    def test_placeholder_missing(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "[0x80] [0x81]"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "[0x80] [0x81]", translation="[0x80]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("sequence mismatch" in e for e in result["errors"]))
    def test_placeholder_duplicated(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "[0x80]"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "[0x80]", translation="[0x80] [0x80]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("sequence mismatch" in e for e in result["errors"]))
    def test_unknown_placeholder(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "PRESS [0x80]"
        trans = _make_translated([_rec(0, "PRESS [0x80]", translation="PRESSIONA [0x90]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("unknown placeholder" in e for e in result["errors"]))
    def test_invalid_hex_placeholder(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "PRESS [0x8G]"
        trans = _make_translated([_rec(0, "PRESS [0x8G]", translation="PRESSIONA [0x8G]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("unknown placeholder" in e for e in result["errors"]))
    def test_empty_bracket_token(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "PRESS [0x80]"
        trans = _make_translated([_rec(0, "PRESS [0x80]", translation="PRESSIONA [0x]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("unknown placeholder" in e for e in result["errors"]))
    def test_punctuation_bracket_token(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "PRESS [0x80]"
        trans = _make_translated([_rec(0, "PRESS [0x80]", translation="PRESSIONA [0x-]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("unknown placeholder" in e for e in result["errors"]))
    def test_extra_malformed_token_no_source(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "PRESS [0x80]"
        trans = _make_translated([_rec(0, "PRESS [0x80]", translation="PRESSIONA [0x80] [0x80-foo]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("unknown placeholder" in e for e in result["errors"]))
    def test_raw_u007f_preserved(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "PRESS \x7f TO PLAY"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "PRESS \x7f TO PLAY", translation="PRESSIONA \x7f PARA JOGAR", byte_length=15)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_raw_u007f_missing(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "PRESS \x7f TO PLAY"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "PRESS \x7f TO PLAY", translation="PRESSIONA PARA JOGAR")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("sequence mismatch" in e for e in result["errors"]))
    def test_newline_run_changed(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "LINE1\n\nLINE3"
        trans = _make_translated([_rec(0, "LINE1\n\nLINE3", translation="LINHA1\nLINHA3")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("newline-run structure mismatch" in e for e in result["errors"]))
    def test_newline_run_preserved(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "LINE1\n\nLINE3"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "LINE1\n\nLINE3", translation="LINHA1\n\nLINHA3", byte_length=12)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_cp1252_unencodable_emoji(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["encoding"] = "cp1252"; src["strings"][0]["text"] = "HELLO"
        trans = _make_translated([_rec(0, "HELLO", translation="HELLO \U0001F60A")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("not encodable" in e for e in result["errors"]))
    def test_valid_cp1252_accents(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["encoding"] = "cp1252"; src["strings"][0]["text"] = "HELLO"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "HELLO", translation="HOLÁ ÇÃO ÉÍÓ", byte_length=5)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_valid_utf16_unicode(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["encoding"] = "utf-16-be"; src["strings"][0]["text"] = "HELLO"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "HELLO", translation="HOLÁ ÇÃO ÉÍÓ", byte_length=5, encoding="utf-16-be")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_invalid_encoding(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["encoding"] = "latin-1"; src["strings"][0]["text"] = "HELLO"
        trans = _make_translated([_rec(0, "HELLO", translation="HOLÁ")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("not encodable" in e for e in result["errors"]))
    def test_utf16be_unpaired_surrogate_rejected(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["encoding"] = "utf-16-be"; src["strings"][0]["text"] = "HELLO"
        # Unpaired surrogate cannot be encoded in utf-16-be
        trans = _make_translated([_rec(0, "HELLO", translation="\ud800")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("not encodable" in e for e in result["errors"]))
    def test_mixed_raw_token_reordered_fails(self):
        src = _make_source(en_count=1, non_en_count=0)
        src["strings"][0]["text"] = "A \x7f B [0x80] C"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "A \x7f B [0x80] C", translation="X [0x80] Y \x7f Z", byte_length=17)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("sequence mismatch" in e for e in result["errors"]))
    def test_valid_translated_surrounding_raw_u007f(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["text"] = "A \x7f B"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "A \x7f B", translation="X \x7f Y")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_lowercased_token_mismatch(self):
        src = _make_source(en_count=1, non_en_count=0)
        src["strings"][0]["text"] = "PRESS [0x8A]"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "PRESS [0x8A]", translation="PRESSIONA [0x8a]")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("sequence mismatch" in e for e in result["errors"]))
    def test_cp1252_u2019_curly_apostrophe(self):
        src = _make_source(en_count=1, non_en_count=0); src["strings"][0]["encoding"] = "cp1252"; src["strings"][0]["text"] = "BANJO\u2019S"; src["strings"][0]["byte_length"] = len(src["strings"][0]["text"])
        trans = _make_translated([_rec(0, "BANJO\u2019S", translation="BANJO\u2019S", byte_length=7)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])


class TestGate5Duplicate(unittest.TestCase):
    def test_duplicate_mismatch(self):
        src = _make_source(en_count=3, non_en_count=0)
        src["strings"][1]["text"] = "DUPLICATE_TEXT"; src["strings"][1]["byte_length"] = len("DUPLICATE_TEXT")
        src["strings"][2]["text"] = "DUPLICATE_TEXT"; src["strings"][2]["byte_length"] = len("DUPLICATE_TEXT")
        trans = _make_translated([_rec(0, "UNIQUE_TEXT", translation="UNIQUE_PT"), _rec(1, "DUPLICATE_TEXT", translation="DUPLICATE_PT_A", byte_length=14), _rec(2, "DUPLICATE_TEXT", translation="DUPLICATE_PT_B", byte_length=14)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("inconsistency" in e for e in result["errors"]))
    def test_duplicate_match(self):
        src = _make_source(en_count=3, non_en_count=0)
        src["strings"][1]["text"] = "DUPLICATE_TEXT"; src["strings"][1]["byte_length"] = len("DUPLICATE_TEXT")
        src["strings"][2]["text"] = "DUPLICATE_TEXT"; src["strings"][2]["byte_length"] = len("DUPLICATE_TEXT")
        trans = _make_translated([_rec(0, "EN_STRING_0", translation="UNIQUE_PT"), _rec(1, "DUPLICATE_TEXT", translation="DUPLICATE_PT", byte_length=14), _rec(2, "DUPLICATE_TEXT", translation="DUPLICATE_PT", byte_length=14)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
    def test_null_peer_no_inconsistency(self):
        src = _make_source(en_count=3, non_en_count=0)
        src["strings"][1]["text"] = "DUPLICATE_TEXT"; src["strings"][1]["byte_length"] = len("DUPLICATE_TEXT")
        src["strings"][2]["text"] = "DUPLICATE_TEXT"; src["strings"][2]["byte_length"] = len("DUPLICATE_TEXT")
        trans = _make_translated([_rec(0, "EN_STRING_0", translation="UNIQUE_PT"), _rec(1, "DUPLICATE_TEXT", translation=None, byte_length=14), _rec(2, "DUPLICATE_TEXT", translation="DUPLICATE_PT", byte_length=14)])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(result["errors"], [])


class TestGate6CLIPassthrough(unittest.TestCase):
    def test_cli_pass_exit_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = _make_source(en_count=2, non_en_count=1)
            sp = os.path.join(tmpdir, "source.json")
            with open(sp, "w", encoding="utf-8") as f: json.dump(src, f)
            trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation="PT_ONE"), _rec(1521, "NONEN_STRING_0", offset=0x8EB4 + 2 * 10)])
            tp = os.path.join(tmpdir, "translated.json")
            with open(tp, "w", encoding="utf-8") as f: json.dump(trans, f)
            r = subprocess.run([sys.executable, os.path.join(_PROJECT_ROOT, "tools", "validate_translation.py"), "--source", sp, "--translated", tp, "--allow-incomplete"], capture_output=True, text=True, cwd=_PROJECT_ROOT)
            self.assertEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
            self.assertIn("PASS", r.stdout)
    def test_cli_fail_exit_nonzero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = _make_source(en_count=2, non_en_count=1)
            sp = os.path.join(tmpdir, "source.json")
            with open(sp, "w", encoding="utf-8") as f: json.dump(src, f)
            trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=""), _rec(1521, "NONEN_STRING_0")])
            tp = os.path.join(tmpdir, "translated.json")
            with open(tp, "w", encoding="utf-8") as f: json.dump(trans, f)
            r = subprocess.run([sys.executable, os.path.join(_PROJECT_ROOT, "tools", "validate_translation.py"), "--source", sp, "--translated", tp, "--allow-incomplete"], capture_output=True, text=True, cwd=_PROJECT_ROOT)
            self.assertNotEqual(r.returncode, 0, f"stdout={r.stdout} stderr={r.stderr}")
            self.assertIn("FAIL", r.stderr)
    def test_cli_pass_summary_counts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            src = _make_source(en_count=3, non_en_count=2)
            sp = os.path.join(tmpdir, "source.json")
            with open(sp, "w", encoding="utf-8") as f: json.dump(src, f)
            trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation="PT_ONE"), _rec(2, "EN_STRING_2", translation="PT_TWO"), _rec(1521, "NONEN_STRING_0", offset=0x8EB4 + 3 * 10), _rec(1522, "NONEN_STRING_1", offset=0x8EB4 + 4 * 10)])
            tp = os.path.join(tmpdir, "translated.json")
            with open(tp, "w", encoding="utf-8") as f: json.dump(trans, f)
            r = subprocess.run([sys.executable, os.path.join(_PROJECT_ROOT, "tools", "validate_translation.py"), "--source", sp, "--translated", tp, "--allow-incomplete"], capture_output=True, text=True, cwd=_PROJECT_ROOT)
            self.assertEqual(r.returncode, 0)
            self.assertIn("total=5", r.stdout)
            self.assertIn("EN=3", r.stdout)
            self.assertIn("translated=2", r.stdout)
            self.assertIn("incomplete=1", r.stdout)
            self.assertIn("non-EN=2", r.stdout)


class TestNonDictRecords(unittest.TestCase):
    def test_non_dict_source_record(self):
        src = _make_source(en_count=2, non_en_count=1)
        src["strings"][1] = "not a dict"
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=None), _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("source is not a dict" in e for e in result["errors"]))
    def test_non_dict_translated_record(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), "not a dict", _rec(1521, "NONEN_STRING_0")])
        result = validate_translation(src, trans, allow_incomplete=True)
        self.assertTrue(any("translated is not a dict" in e for e in result["errors"]))


class TestGate7NoMutation(unittest.TestCase):
    def test_source_not_mutated(self):
        src = _make_source(en_count=2, non_en_count=1); src_copy = copy.deepcopy(src)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=None), _rec(1521, "NONEN_STRING_0")])
        validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(src, src_copy)
    def test_translated_not_mutated(self):
        src = _make_source(en_count=2, non_en_count=1)
        trans = _make_translated([_rec(0, "EN_STRING_0"), _rec(1, "EN_STRING_1", translation=None), _rec(1521, "NONEN_STRING_0")])
        trans_copy = copy.deepcopy(trans)
        validate_translation(src, trans, allow_incomplete=True)
        self.assertEqual(trans, trans_copy)


class TestRealDataIntegration(unittest.TestCase):
    def test_init_result_passes_allow_incomplete(self):
        from tools.init_translation import build_tm_lookup, init_translation, load_json
        source_data = load_json(os.path.join(_PROJECT_ROOT, "translation", "pt-BR", "source.json"))
        tm_data = load_json(os.path.join(_PROJECT_ROOT, "translation", "pt-BR", "tm.json"))
        tm_lookup = build_tm_lookup(tm_data)
        translated_data = init_translation(source_data, tm_lookup)
        en_count = sum(1 for e in translated_data["strings"] if e["index"] < 1521)
        translated_count = sum(1 for e in translated_data["strings"] if e["index"] < 1521 and e.get("translation") is not None)
        incomplete_count = en_count - translated_count
        result = validate_translation(source_data, translated_data, allow_incomplete=True)
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["counts"]["EN"], en_count)
        self.assertEqual(result["counts"]["translated"], translated_count)
        self.assertEqual(result["counts"]["incomplete"], incomplete_count)
        self.assertEqual(translated_count, 12, "Expected 12 approved TM entries")
        self.assertEqual(incomplete_count, 1023, "Expected 1023 incomplete EN entries")
    def test_init_result_fails_strict(self):
        from tools.init_translation import build_tm_lookup, init_translation, load_json
        source_data = load_json(os.path.join(_PROJECT_ROOT, "translation", "pt-BR", "source.json"))
        tm_data = load_json(os.path.join(_PROJECT_ROOT, "translation", "pt-BR", "tm.json"))
        tm_lookup = build_tm_lookup(tm_data)
        translated_data = init_translation(source_data, tm_lookup)
        result = validate_translation(source_data, translated_data, allow_incomplete=False)
        self.assertTrue(len(result["errors"]) > 0, "Expected strict mode to fail")
        for err in result["errors"]:
            self.assertIn("null translation", err, f"Unexpected error: {err}")
    def test_no_canonical_output_written(self):
        from tools.init_translation import build_tm_lookup, init_translation, load_json
        source_data = load_json(os.path.join(_PROJECT_ROOT, "translation", "pt-BR", "source.json"))
        tm_data = load_json(os.path.join(_PROJECT_ROOT, "translation", "pt-BR", "tm.json"))
        tm_lookup = build_tm_lookup(tm_data)
        translated_data = init_translation(source_data, tm_lookup)
        before_files = set(os.listdir(os.path.join(_PROJECT_ROOT, "translation", "pt-BR")))
        validate_translation(source_data, translated_data, allow_incomplete=True)
        after_files = set(os.listdir(os.path.join(_PROJECT_ROOT, "translation", "pt-BR")))
        self.assertEqual(before_files, after_files, "validate_translation wrote files!")


if __name__ == "__main__":
    unittest.main(verbosity=2)
