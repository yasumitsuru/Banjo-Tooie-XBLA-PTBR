#!/usr/bin/env python3
"""Validate a translated.json against its source.json.

CLI defaults:
    --source      translation/pt-BR/source.json
    --translated  translation/pt-BR/translated.json
    --allow-incomplete   (permit EN entries with null translation)

Exit codes:
    0  PASS
    1  FAIL (errors reported to stderr)

Stdlib only. Never mutates inputs or writes files.
"""
import argparse
import json
import re
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EN_BOUNDARY = 1521  # index < 1521 is EN

# Valid controller placeholders: [0x80] .. [0x8F] (uppercase hex only)
_VALID_PH = set(f"[0x{i:02X}]" for i in range(0x80, 0x90))
_PH_ANY_RE = re.compile(r"\[0x[^]]*\]")
_COMBINED_RE = re.compile(r"\[0x[0-9A-Fa-f]+\]|\x7f")

# ---------------------------------------------------------------------------
# Public helpers (exposed for testing)
# ---------------------------------------------------------------------------


def _load_json(path: str) -> dict:
    """Load a strict UTF-8 JSON file and return the parsed dict."""
    with open(path, "rb") as f:
        raw = f.read()
    raw.decode("utf-8")  # strict UTF-8 validation
    return json.loads(raw)


def _newline_runs(text: str) -> list:
    """Return ordered list of run lengths of consecutive \\n in text."""
    runs = []
    count = 0
    for ch in text:
        if ch == "\n":
            count += 1
        else:
            if count:
                runs.append(count)
                count = 0
    if count:
        runs.append(count)
    return runs


def _encodable(text: str, encoding: str) -> bool:
    """Check whether *text* can be encoded in the given encoding."""
    if encoding == "cp1252":
        try:
            text.encode("cp1252")
            return True
        except UnicodeEncodeError:
            return False
    if encoding == "utf-16-be":
        try:
            text.encode("utf-16-be")
            return True
        except (UnicodeEncodeError, UnicodeDecodeError):
            return False
    return False


def _check_placeholders(source_text: str, translation: str) -> list:
    """Check that translation preserves the exact ordered sequence of
    controller placeholders and raw U+007F from source_text.

    Walks each string left-to-right and returns combined markers
    ([0x80]…[0x8F] exact token strings and raw \x7f); compares
    source/translation combined sequences exactly.

    Returns a list of error strings (empty if valid).
    """
    errors = []

    def _scan_markers(text: str) -> list:
        """Return ordered list of (type, exact_token) from left-to-right scan."""
        markers = []
        for m in _COMBINED_RE.finditer(text):
            token = m.group(0)
            if token == "\x7f":
                markers.append(("cr", "\x7f"))
            else:
                markers.append(("ph", token))
        return markers

    src_markers = _scan_markers(source_text)
    trans_markers = _scan_markers(translation)

    # Check unknown placeholders in translation
    for m in _PH_ANY_RE.finditer(translation):
        ph = m.group(0)
        if ph not in _VALID_PH:
            errors.append(f"unknown placeholder {ph!r} in translation")

    # Check exact ordered combined sequence matches
    if src_markers != trans_markers:
        errors.append(
            f"marker sequence mismatch: "
            f"source={src_markers!r} vs translation={trans_markers!r}"
        )

    return errors


def validate_translation(
    source_data: dict,
    translated_data: dict,
    allow_incomplete: bool = False,
) -> dict:
    """Validate translated.json against source.json.

    Returns a dict with:
        errors: list of error strings
        counts: dict with total/EN/translated/incomplete/non-EN counts
    """
    errors: list[str] = []
    counts = {"total": 0, "EN": 0, "translated": 0, "incomplete": 0, "non-EN": 0}

    # ---- Gate 1: Strict UTF-8/JSON object inputs with `strings` list ----
    # (caller handles file loading; we validate structure here)
    if not isinstance(source_data, dict):
        errors.append("source is not a JSON object")
        return {"errors": errors, "counts": counts}
    if not isinstance(translated_data, dict):
        errors.append("translated is not a JSON object")
        return {"errors": errors, "counts": counts}
    if "strings" not in source_data:
        errors.append("source missing 'strings'")
        return {"errors": errors, "counts": counts}
    if "strings" not in translated_data:
        errors.append("translated missing 'strings'")
        return {"errors": errors, "counts": counts}
    if not isinstance(source_data["strings"], list):
        errors.append("source['strings'] is not a list")
        return {"errors": errors, "counts": counts}
    if not isinstance(translated_data["strings"], list):
        errors.append("translated['strings'] is not a list")
        return {"errors": errors, "counts": counts}

    src_strings = source_data["strings"]
    trans_strings = translated_data["strings"]

    # ---- Gate 2a: Structural integrity - top-level keys ----
    src_keys = list(source_data.keys())
    trans_keys = list(translated_data.keys())
    if src_keys != trans_keys:
        errors.append(
            f"top-level key mismatch: source={src_keys!r} vs "
            f"translated={trans_keys!r}"
        )

    # ---- Gate 2b: Structural integrity - metadata values ----
    for key in src_keys:
        if key == "strings":
            continue
        if source_data[key] != translated_data.get(key):
            errors.append(
                f"metadata '{key}' mismatch: "
                f"source={source_data[key]!r} vs "
                f"translated={translated_data.get(key)!r}"
            )

    # ---- Gate 2c: Structural integrity - record count and order ----
    src_count = len(src_strings)
    trans_count = len(trans_strings)
    if src_count != trans_count:
        errors.append(
            f"record count mismatch: source={src_count} vs "
            f"translated={trans_count}"
        )

    # ---- Gate 3: Scope - EN vs non-EN ----
    # Count totals
    counts["total"] = trans_count
    counts["EN"] = 0
    counts["non-EN"] = 0

    # ---- Gate 2d: Per-record source fields/values ----
    # Required core fields present in every source record
    _REQUIRED_CORE = {"index", "offset", "byte_length", "encoding", "text"}

    min_len = min(src_count, trans_count)
    for i in range(min_len):
        src_rec = src_strings[i]
        trans_rec = trans_strings[i]

        # Source must be a dict with all required core fields
        if not isinstance(src_rec, dict):
            errors.append(f"record {i} (index={i}): source is not a dict")
            continue
        idx = src_rec.get("index", i)
        missing_core = _REQUIRED_CORE - set(src_rec.keys())
        if missing_core:
            errors.append(
                f"record {i} (index={idx}): "
                f"source missing required fields: {sorted(missing_core)!r}"
            )
            continue

        # Translated must be a dict; expected keys = source keys + 'translation'
        if not isinstance(trans_rec, dict):
            errors.append(f"record {i} (index={idx}): translated is not a dict")
            continue

        trans_keys = set(trans_rec.keys())
        src_keys = set(src_rec.keys())
        expected_trans_keys = src_keys | {"translation"}

        # Reject translated-only extra keys
        extra_trans = trans_keys - expected_trans_keys
        if extra_trans:
            errors.append(
                f"record {i} (index={idx}): "
                f"translated has extra keys not in source: {sorted(extra_trans)!r}"
            )

        # Reject omitted arbitrary source keys
        missing_from_trans = src_keys - trans_keys
        if missing_from_trans:
            errors.append(
                f"record {i} (index={idx}): "
                f"translated omits source keys: {sorted(missing_from_trans)!r}"
            )

        # Check translation field exists
        if "translation" not in trans_rec:
            errors.append(
                f"record {i} (index={idx}): "
                f"missing 'translation' field"
            )
            continue

        # Compare every source field value generically
        for field in src_keys:
            if src_rec[field] != trans_rec.get(field):
                errors.append(
                    f"record {i} (index={idx}): "
                    f"'{field}' mismatch: "
                    f"source={src_rec[field]!r} vs "
                    f"translated={trans_rec.get(field)!r}"
                )

        translation = trans_rec["translation"]

        # ---- Gate 3: non-EN must have null translation ----
        if idx >= EN_BOUNDARY:
            if translation is not None:
                errors.append(
                    f"record {i} (index={idx}): "
                    f"non-EN entry has non-null translation "
                    f"{translation!r}"
                )
            counts["non-EN"] += 1
            continue

        # EN range
        counts["EN"] += 1
        src_text = src_rec.get("text", "")

        # ---- Gate 4a: Empty/whitespace/non-string translation ----
        if translation is not None:
            if not isinstance(translation, str):
                errors.append(
                    f"record {i} (index={idx}): "
                    f"translation is not a string: {type(translation).__name__}"
                )
                continue
            if translation.strip() == "":
                errors.append(
                    f"record {i} (index={idx}): "
                    f"translation is empty or whitespace only"
                )
                continue

            # ---- Gate 4b: Reject U+FFFD ----
            if "\ufffd" in translation:
                errors.append(
                    f"record {i} (index={idx}): "
                    f"translation contains U+FFFD (replacement character)"
                )

            # ---- Gate 4c: Reject CR ----
            if "\r" in translation:
                errors.append(
                    f"record {i} (index={idx}): "
                    f"translation contains carriage return (CR)"
                )

            # ---- Gate 4d: Placeholder preservation ----
            ph_errors = _check_placeholders(src_text, translation)
            for pe in ph_errors:
                errors.append(f"record {i} (index={idx}): {pe}")

            # ---- Gate 4e: Newline-run structure ----
            src_nl = _newline_runs(src_text)
            trans_nl = _newline_runs(translation)
            if src_nl != trans_nl:
                errors.append(
                    f"record {i} (index={idx}): "
                    f"newline-run structure mismatch: "
                    f"source={src_nl!r} vs "
                    f"translation={trans_nl!r}"
                )

            # ---- Gate 4f: Encodability ----
            enc = src_rec.get("encoding", "cp1252")
            if not _encodable(translation, enc):
                errors.append(
                    f"record {i} (index={idx}): "
                    f"translation not encodable in {enc}"
                )

            counts["translated"] += 1
        else:
            # null translation
            if not allow_incomplete:
                errors.append(
                    f"record {i} (index={idx}): "
                    f"EN entry has null translation (strict mode)"
                )
            counts["incomplete"] += 1

    # Handle extra records in translated
    if trans_count > src_count:
        for i in range(src_count, trans_count):
            errors.append(
                f"record {i}: extra record in translated (no source match)"
            )

    # ---- Gate 5: Duplicate consistency ----
    # Among EN records with identical source text and non-null translations,
    # translations must be identical
    src_text_to_translations: dict[str, list[tuple[int, int, str]]] = {}
    for i in range(min_len):
        trans_rec = trans_strings[i]
        if not isinstance(trans_rec, dict):
            continue
        if "translation" not in trans_rec:
            continue
        translation = trans_rec["translation"]
        if translation is None or not isinstance(translation, str):
            continue
        idx = trans_rec.get("index", i)
        if idx >= EN_BOUNDARY:
            continue
        src_rec_i = src_strings[i]
        if not isinstance(src_rec_i, dict):
            continue
        src_text = src_rec_i.get("text", "")
        if src_text not in src_text_to_translations:
            src_text_to_translations[src_text] = []
        src_text_to_translations[src_text].append(
            (i, idx, translation)
        )

    for src_text, entries in src_text_to_translations.items():
        if len(entries) < 2:
            continue
        first_trans = entries[0][2]
        for rec_idx, rec_src_idx, trans in entries[1:]:
            if trans != first_trans:
                errors.append(
                    f"duplicate source text inconsistency: "
                    f"source={src_text!r} -> "
                    f"index {entries[0][1]}={first_trans!r} vs "
                    f"index {rec_src_idx}={trans!r}"
                )

    # ---- Gate 5b: In allow-incomplete, null peers don't create inconsistency ----
    # (already handled above by skipping null translations)

    counts["incomplete"] = sum(
        1 for i in range(min_len)
        if i < src_count
        and isinstance(trans_strings[i], dict)
        and trans_strings[i].get("index", i) < EN_BOUNDARY
        and trans_strings[i].get("translation") is None
    )
    counts["translated"] = sum(
        1 for i in range(min_len)
        if i < src_count
        and isinstance(trans_strings[i], dict)
        and trans_strings[i].get("index", i) < EN_BOUNDARY
        and trans_strings[i].get("translation") is not None
    )

    return {"errors": errors, "counts": counts}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--source",
        default="translation/pt-BR/source.json",
        help="Path to source.json",
    )
    ap.add_argument(
        "--translated",
        default="translation/pt-BR/translated.json",
        help="Path to translated.json",
    )
    ap.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow EN entries with null translation",
    )
    args = ap.parse_args()

    # Load inputs
    try:
        source_data = _load_json(args.source)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"ERROR: cannot load source: {exc}", file=sys.stderr)
        sys.exit(1)
    try:
        translated_data = _load_json(args.translated)
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        print(f"ERROR: cannot load translated: {exc}", file=sys.stderr)
        sys.exit(1)

    # Validate
    result = validate_translation(
        source_data, translated_data, allow_incomplete=args.allow_incomplete
    )

    errors = result["errors"]
    counts = result["counts"]

    if errors:
        for err in errors:
            print(f"ERROR: {err}", file=sys.stderr)
        print(
            f"\nFAIL: {len(errors)} error(s) found",
            file=sys.stderr,
        )
        print(
            f"total={counts['total']} EN={counts['EN']} "
            f"translated={counts['translated']} "
            f"incomplete={counts['incomplete']} "
            f"non-EN={counts['non-EN']}",
            file=sys.stderr,
        )
        sys.exit(1)
    else:
        print(
            f"PASS: total={counts['total']} EN={counts['EN']} "
            f"translated={counts['translated']} "
            f"incomplete={counts['incomplete']} "
            f"non-EN={counts['non-EN']}"
        )
        sys.exit(0)


if __name__ == "__main__":
    main()
