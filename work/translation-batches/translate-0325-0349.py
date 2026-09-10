#!/usr/bin/env python3
"""Translate source indices 325..349 to pt-BR and produce batch artifact + merge.

Deterministic: running twice produces byte-identical output.

Terminology decisions for this batch:
  - TRASH CAN GERMS (325): nome de mini-jogo — manter em inglês
    (glossário: "TRASH CAN GERMS").
  - MAYAHEM TEMPLE (328): nome próprio de fase — manter em inglês
    (glossário: "Mayahem Temple").
  - GLITTER GULCH MINE (329): nome próprio de fase — manter em inglês
    (glossário: "Glitter Gulch Mine").
  - WITCHYWORLD (330): nome próprio de fase — manter em inglês
    (glossário: "Witchy World").
  - JOLLY ROGER'S LAGOON (331): nome próprio de fase — manter em inglês
    (glossário: "JOLLY ROGER'S LAGOON").
  - TERRYDACTYLAND (332): nome próprio de fase — manter em inglês
    (glossário: "TERRYDACTYLAND").
  - GRUNTY INDUSTRIES (333): nome próprio de fase — manter em inglês
    (glossário: "Grunty Industries").
  - HAILFIRE PEAKS (334): nome próprio de fase — manter em inglês
    (glossário: "Hailfire Peaks").
  - CLOUD CUCKOOLAND (335): nome próprio de fase — manter em inglês
    (glossário: "Cloud Cuckooland").
  - FLIP Y AXIS: "INVERTIR EIXO Y" — termo de UI.
  - PREVIOUS BEST: "MELHOR ANTERIOR" — label de UI.
  - Continue without saving (346): "Continuar sem salvar" — caixa mista,
    idêntico ao índice 189 (política de preservação de caixa).
  - DOUBLOON GAMER PICTURE (348): "DOBRÃO" — moeda comum (doubloon) traduzida
    para pt-BR, seguindo a política de itens descritivos e o padrão
    multilíngue (FR DOUBLON, ES DOBLÓN, IT DOBLONE). Fonte: Wiktionary pt
    (dobrão = antiga moeda de ouro/doubloon). Mantém o artigo "DO" para
    consistência com 349.
  - STOP 'N' SWOP (349): franquia — nome próprio mantido em inglês
    (glossário: "STOP 'N' SWOP").

Expected after filling all 25 new indices (no approved seeds in-range):
  - EN translated: 350 (325 + 25)
  - EN incomplete: 685 (710 - 25)
"""

import json
import os
import sys

# ── Translations ──────────────────────────────────────────────────────────
TRANSLATIONS = {
    325: " JOGO DO TRASH CAN GERMS",
    326: " ENCONTRAR A COMBINAÇÃO DO COFRE",
    327: " DENTRO DO CASTELO DE GELATINA",
    328: "MAYAHEM TEMPLE",
    329: "GLITTER GULCH MINE",
    330: "WITCHYWORLD",
    331: "JOLLY ROGER'S LAGOON",
    332: "TERRYDACTYLAND",
    333: "GRUNTY INDUSTRIES",
    334: "HAILFIRE PEAKS",
    335: "CLOUD CUCKOOLAND",
    336: "INVERTIR EIXO Y : NÃO",
    337: "INVERTIR EIXO Y : SIM",
    338: "MELHOR ANTERIOR :",
    339: "Carregando...",
    340: "Por favor, faça login",
    341: "Este jogo requer que você faça login em um perfil de jogador para jogar",
    342: "OK",
    343: "Nenhum dispositivo selecionado",
    344: "Se você não selecionar um dispositivo, os salvamentos do jogo serão desabilitados",
    345: "Selecionar um dispositivo",
    346: "Continuar sem salvar",
    347: "REINSTALAR EXTRAS",
    348: "REINSTALAR IMAGEM DE JOGADOR DO DOBRÃO",
    349: "REINSTALAR IMAGEM DE JOGADOR DO STOP 'N' SWOP",
}

EXPECTED_RANGE = set(range(325, 350))
if set(TRANSLATIONS) != EXPECTED_RANGE:
    raise RuntimeError("TRANSLATIONS must contain exactly indices 325..349")

# ── Load source ───────────────────────────────────────────────────────────
with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

expected_indices = list(range(325, 350))
actual_indices = sorted([s["index"] for s in src_strings if 325 <= s["index"] <= 349])
if actual_indices != expected_indices:
    print(f"ERROR: Expected indices {expected_indices}, got {actual_indices}")
    sys.exit(1)
print(f"Source indices 325..349: {len(actual_indices)} entries found")

# ── Build batch artifact ──────────────────────────────────────────────────
batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 325 <= idx <= 349:
        batch_entries.append({
            "index": idx,
            "source_text": s["text"],
            "translation": TRANSLATIONS[idx],
        })

# Fail before writing any generated artifact when the in-memory batch is invalid.
source_by_index = {s["index"]: s for s in src_strings}
preflight_source_errors = []
preflight_structure_errors = []
preflight_blank_translations = []
preflight_cp1252_errors = []
for entry in batch_entries:
    idx = entry["index"]
    src_rec = source_by_index.get(idx)
    translation = entry["translation"]
    if src_rec is None or src_rec["text"] != entry["source_text"]:
        preflight_source_errors.append(idx)
    if not isinstance(translation, str) or not translation.strip():
        preflight_blank_translations.append(idx)
        continue
    source_text = entry["source_text"]
    if (translation[:len(translation) - len(translation.lstrip())]
            != source_text[:len(source_text) - len(source_text.lstrip())]
            or translation.count("\n") != source_text.count("\n")):
        preflight_structure_errors.append(idx)
    try:
        translation.encode("cp1252")
    except UnicodeEncodeError as e:
        preflight_cp1252_errors.append((idx, str(e)))

if (preflight_source_errors or preflight_structure_errors
        or preflight_blank_translations or preflight_cp1252_errors):
    print("ERROR: batch preflight failed before artifact writes")
    print(f"  Source mismatches: {preflight_source_errors}")
    print(f"  Leading-space/newline mismatches: {preflight_structure_errors}")
    print(f"  Blank translations: {preflight_blank_translations}")
    for idx, err in preflight_cp1252_errors:
        print(f"  cp1252 index {idx}: {err}")
    raise RuntimeError("batch preflight failed before writing artifacts")
print("Preflight passed: source, structure, and cp1252")

batch_artifact = {
    "batch_id": "batch-0325-0349",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": list(range(325, 350)),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0325-0349.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")

# ── Merge into translated.json ────────────────────────────────────────────
with open("translation/pt-BR/translated.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

trans_map = {idx: TRANSLATIONS[idx] for idx in range(325, 350)}
merged_count = 0
for i, rec in enumerate(trans_data["strings"]):
    idx = rec.get("index", i)
    if idx in trans_map:
        trans_data["strings"][i]["translation"] = trans_map[idx]
        merged_count += 1

merged_path = "translation/pt-BR/translated.json"
with open(merged_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(trans_data, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
if merged_count != len(expected_indices):
    raise RuntimeError(f"Expected to merge 25 records, merged {merged_count}")
print(f"Merged {merged_count} translations into {merged_path}")

# ── Verification ──────────────────────────────────────────────────────────
with open(merged_path, "r", encoding="utf-8") as f:
    verify_data = json.load(f)
vs = verify_data["strings"]

translated_in_range = [s for s in vs if 325 <= s["index"] <= 349 and s.get("translation") is not None]
incomplete_in_range = [s for s in vs if 325 <= s["index"] <= 349 and s.get("translation") is None]
all_translated = [s for s in vs if s.get("translation") is not None]
all_incomplete = [s for s in vs if s.get("translation") is None]
en_strings = [s for s in vs if s["index"] < 1521]
non_en = [s for s in vs if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"")
print(f"Verification:")
print(f"  Translated in range 325..349: {len(translated_in_range)}")
print(f"  Incomplete in range 325..349: {len(incomplete_in_range)}")
print(f"")
print(f"Totals:")
print(f"  Total strings: {len(vs)}")
print(f"  Translated: {len(all_translated)}")
print(f"  Incomplete: {len(all_incomplete)}")
print(f"  EN (0-1520): {len(en_strings)}")
print(f"  Non-EN: {len(non_en)}")

assigned = [s["index"] for s in batch_entries]
print(f"")
print(f"No duplicates: {len(assigned) == len(set(assigned))}")

null_trans = [e for e in batch_entries if not e["translation"]]
blank_trans = [e for e in batch_entries if e["translation"].strip() == ""]
print(f"Null translations in batch: {len(null_trans)}")
print(f"Blank translations in batch: {len(blank_trans)}")

mismatch = []
structure_errors = []
for entry in batch_entries:
    idx = entry["index"]
    src_rec = next((s for s in src_strings if s["index"] == idx), None)
    if src_rec and src_rec["text"] != entry["source_text"]:
        mismatch.append(idx)
    if src_rec and (entry["translation"][:len(entry["translation"]) - len(entry["translation"].lstrip())]
                    != src_rec["text"][:len(src_rec["text"]) - len(src_rec["text"].lstrip())]
                    or entry["translation"].count("\n") != src_rec["text"].count("\n")):
        structure_errors.append(idx)
print(f"Source text mismatches: {len(mismatch)}")
print(f"Leading-space/newline mismatches: {len(structure_errors)}")
if mismatch or structure_errors or null_trans or blank_trans:
    raise RuntimeError("batch source/translation invariants failed")

cp1252_errors = []
for entry in batch_entries:
    try:
        entry["translation"].encode("cp1252")
    except UnicodeEncodeError as e:
        cp1252_errors.append((entry["index"], str(e)))
if cp1252_errors:
    print(f"")
    print(f"ERROR: cp1252 errors:")
    for idx, err in cp1252_errors:
        print(f"  Index {idx}: {err}")
    raise RuntimeError("batch contains translations that cannot be encoded as cp1252")
else:
    print(f"")
    print(f"All translations are cp1252 compatible")

print(f"")
print(f"Expected post-merge counts:")
print(f"  Total: {len(vs)} (expected 5174) {'OK' if len(vs) == 5174 else 'MISMATCH'}")
print(f"  Translated: {len(all_translated)} (expected 350) {'OK' if len(all_translated) == 350 else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected 685) {'OK' if len(en_incomplete) == 685 else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected 1035) {'OK' if len(en_strings) == 1035 else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected 4139) {'OK' if len(non_en) == 4139 else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")
if (len(vs), len(all_translated), len(en_incomplete), len(en_strings),
        len(non_en), len(non_en_translated)) != (5174, 350, 685, 1035, 4139, 0):
    raise RuntimeError("post-merge count invariants failed")

# ── Selective TM upsert ───────────────────────────────────────────────────
# Only concise, canonical location/item labels are reusable TM candidates.
# One-off objective sentences and UI strings stay in the batch/glossary.
SELECTIVE_TM_NOTES = {
    325: 'mini-jogo — TRASH CAN GERMS (nome próprio de mini-jogo)',
    326: 'objetivo — FIND THE SAFE\'S COMBINATION (frase única, não reutilizável)',
    327: 'localização — JELLY CASTLE (termo descritivo)',
    336: 'UI — FLIP Y AXIS (INVERTIR EIXO Y)',
    337: 'UI — FLIP Y AXIS (INVERTIR EIXO Y)',
    338: 'UI label — PREVIOUS BEST (MELHOR ANTERIOR)',
    340: 'UI — Please sign in (Faça login)',
    341: 'UI — sign in / gamer profile (padrão de login Xbox)',
    346: 'UI — Continue without saving (Continuar sem salvar)',
}

new_tm_entries = []
for idx in sorted(SELECTIVE_TM_NOTES):
    src_rec = next((s for s in src_strings if s["index"] == idx), None)
    if src_rec:
        new_tm_entries.append({
            "source": src_rec["text"],
            "translation": TRANSLATIONS[idx],
            "status": "proposed",
            "source_index": idx,
            "notes": f"batch 0325-0349 - {SELECTIVE_TM_NOTES[idx]}",
        })

tm_path = "translation/pt-BR/tm.json"
with open(tm_path, "r", encoding="utf-8") as f:
    tm_data = json.load(f)

# Remove only this batch's proposed entries that are no longer selected; approved
# entries are immutable. This makes the policy and reruns deterministic.
tm_data["entries"] = [
    e for e in tm_data["entries"]
    if not (325 <= e.get("source_index", -1) <= 349
            and e.get("status") == "proposed"
            and e.get("notes", "").startswith("batch 0325-0349 -"))
]
existing_sources = {e["source"] for e in tm_data["entries"]}
by_pair = {(e["source"], e.get("source_index")): e for e in tm_data["entries"]}
added_count = 0
updated_count = 0
for entry in new_tm_entries:
    pair = (entry["source"], entry["source_index"])
    if pair in by_pair:
        existing = by_pair[pair]
        if existing.get("status") == "approved":
            if existing["translation"] != entry["translation"]:
                raise RuntimeError(f"refusing to alter approved TM entry {entry['source_index']}")
        else:
            existing["translation"] = entry["translation"]
            existing["notes"] = entry["notes"]
        updated_count += 1
    elif entry["source"] not in existing_sources:
        tm_data["entries"].append(entry)
        existing_sources.add(entry["source"])
        by_pair[pair] = entry
        added_count += 1

with open(tm_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(tm_data, f, ensure_ascii=False, indent=2, sort_keys=False)
    f.write("\n")
print(f"")
print(f"TM: added {added_count} new, updated {updated_count} existing (total: {len(tm_data['entries'])})")

en_translated_count = len([s for s in en_strings if s.get("translation") is not None])
print(f"")
print(f"Final EN counts: translated={en_translated_count} incomplete={len(en_incomplete)}")
print("")
print("Done.")
