#!/usr/bin/env python3
"""Initialize translation/pt-BR/translated.json from source.json + tm.json.

Seeds approved translation-memory entries into a copy of source.json,
adding a ``translation`` field per entry.  Only approved entries whose
``source_index`` falls in the EN range (index < 1521) and whose source
string matches exactly are applied.

Usage:
    python tools/init_translation.py [--source PATH] [--tm PATH] [--out PATH] [--force]

Defaults:
    --source  translation/pt-BR/source.json
    --tm      translation/pt-BR/tm.json
    --out     translation/pt-BR/translated.json
"""
import argparse
import json
import os
import sys


# ---------------------------------------------------------------------------
# Public helpers (exposed for testing)
# ---------------------------------------------------------------------------

def load_json(path: str) -> dict:
    """Load a strict UTF-8 JSON file and return the parsed dict."""
    with open(path, "rb") as f:
        raw = f.read()
    raw.decode("utf-8")  # strict UTF-8 validation
    return json.loads(raw)


def build_tm_lookup(tm_data: dict) -> dict:
    """Build a source_index → entry lookup from tm.json entries.

    Returns a dict mapping source_index (int) → entry dict for all
    approved entries.  Raises ValueError on:
      - missing or non-list tm_data['entries']
      - missing source_index, source, or translation field
      - empty translation string
      - duplicate approved source_index.
    Proposed entries are ignored even if malformed.
    """
    entries = tm_data.get("entries")
    if entries is None:
        raise ValueError("tm_data missing 'entries'")
    if not isinstance(entries, list):
        raise ValueError("tm_data['entries'] must be a list")
    lookup = {}
    for entry in entries:
        if entry.get("status") != "approved":
            continue
        idx = entry.get("source_index")
        if idx is None:
            raise ValueError(
                f"approved entry missing source_index: {entry!r}"
            )
        src = entry.get("source")
        if src is None:
            raise ValueError(
                f"approved entry missing source: source_index={idx}"
            )
        trans = entry.get("translation")
        if trans is None:
            raise ValueError(
                f"approved entry missing translation: source_index={idx}"
            )
        if not isinstance(trans, str) or trans == "":
            raise ValueError(
                f"approved entry has empty translation: source_index={idx}"
            )
        if idx in lookup:
            raise ValueError(
                f"duplicate approved source_index {idx} "
                f"(sources: {lookup[idx]['source']!r} vs {entry['source']!r})"
            )
        lookup[idx] = entry
    return lookup


def init_translation(
    source_data: dict,
    tm_lookup: dict,
) -> dict:
    """Create the translated.json structure from source + tm lookup.

    Validates every approved TM entry exists in source and its source
    text exactly matches the source entry.  Only approved entries with
    index < 1521 are seeded; non-EN entries keep translation=null.

    Returns the output dict ready for json.dump (no _meta).
    """
    # Validate source_data['strings'] exists and is a list
    strings = source_data.get("strings")
    if strings is None:
        raise ValueError("source_data missing 'strings'")
    if not isinstance(strings, list):
        raise ValueError("source_data['strings'] must be a list")

    # Validate: all approved TM source_index must exist in source
    source_by_index = {e["index"]: e for e in strings}
    for idx, tm_entry in tm_lookup.items():
        if idx not in source_by_index:
            raise ValueError(
                f"missing approved index {idx}: "
                f"tm.source={tm_entry['source']!r} not in source"
            )
        # Validate source text matches exactly (including non-EN)
        if tm_entry["source"] != source_by_index[idx]["text"]:
            raise ValueError(
                f"stale approved index {idx}: "
                f"tm.source={tm_entry['source']!r} != "
                f"source.text={source_by_index[idx]['text']!r}"
            )

    out_strings = []
    for entry in strings:
        idx = entry["index"]
        # Preserve all per-entry fields via dict copy, then add/replace translation
        out_entry = dict(entry)
        out_entry["translation"] = None

        if idx < 1521:
            # EN range: try to seed from TM
            tm_entry = tm_lookup.get(idx)
            if tm_entry is not None:
                out_entry["translation"] = tm_entry["translation"]

        out_strings.append(out_entry)

    # Preserve generic top-level key order
    result = dict(source_data)
    result["strings"] = out_strings
    return result


def write_output(data: dict, path: str) -> None:
    """Write deterministic UTF-8 JSON to path.

    Creates the parent directory only when dirname(path) is nonempty.
    """
    dirpath = os.path.dirname(path)
    if dirpath:
        os.makedirs(dirpath, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


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
        "--tm",
        default="translation/pt-BR/tm.json",
        help="Path to tm.json",
    )
    ap.add_argument(
        "--out",
        default="translation/pt-BR/translated.json",
        help="Path to output translated.json",
    )
    ap.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing output",
    )
    args = ap.parse_args()

    # Check existing output
    if os.path.exists(args.out) and not args.force:
        print(f"ERROR: output exists: {args.out} (use --force)", file=sys.stderr)
        sys.exit(1)

    # Load inputs
    source_data = load_json(args.source)
    tm_data = load_json(args.tm)

    # Build TM lookup (validates duplicates)
    tm_lookup = build_tm_lookup(tm_data)

    # Run init
    result = init_translation(source_data, tm_lookup)

    # Write output
    write_output(result, args.out)

    # Print concise counts derived from result/source
    total = len(result["strings"])
    en = sum(1 for e in result["strings"] if e["index"] < 1521)
    non_en = total - en
    approved_seeded = sum(
        1 for e in result["strings"]
        if e["index"] < 1521 and e.get("translation") is not None
    )
    en_null = en - approved_seeded
    print(f"total: {total}  EN: {en}  non-EN: {non_en}")
    print(f"approved seeded: {approved_seeded}  EN null: {en_null}")
    print(f"out: {args.out}")


if __name__ == "__main__":
    main()
