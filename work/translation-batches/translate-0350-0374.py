#!/usr/bin/env python3
"""Translate source indices 350..374 to pt-BR and produce batch artifact + merge.

Deterministic: running twice produces byte-identical output.

Terminology decisions for this batch:
  - BANJO THEME (350): "TEMA DO BANJO" — BANJO é nome próprio; a
    preposição torna o nome do tema natural em pt-BR.
  - REINSTALLED/REINSTALLING (351-354): participes progressivos/pretéritos
    padrão pt-BR ("REINSTALADO", "REINSTALANDO").
  - GAMER PICTURE (353): "IMAGEM DE JOGADOR" — consistente com índices
    348/349 do lote anterior.
  - THEME (355, 357): "TEMA" — termo descritivo de UI.
  - Loading failed (358): "Falha ao carregar" — paralelo a "FALHA AO SALVAR"
    (132, 186, 201).
  - storage device (359): "dispositivo de armazenamento" — consistente com
    índice 138 (glossário).
  - WARP / WARP PAD (360, 364): "TELETRANSPORTAR" / "PLATAFORMA DE
    TELETRANSPORTE" — termo natural e consistente para o pad do jogo.
  - MOLE-RESTORING QUEST (366): "MISSÃO DE REANIMAR O BOTTLES" — a
    variante DE da repetição urgente em 398 identifica a toupeira como Bottles
    e confirma reanimação, não resgate; o singular é o contexto do jogo.
  - GRABBING / CLIMB / RELEASE HOLD (369): "ENQUANTO ESTIVER AGARRADO",
    "SUBIR ATÉ A BORDA" e "SOLTAR-SE" — instrução de mecânica de jogo.
  - LEARN THE MOVE / BE DISMISSED (372): "APRENDER O MOVIMENTO" /
    "RECUSAR" — opção natural de negar a oferta; FR/DE/ES corroboram
    cancelar/não aprender/recusar, em vez do passivo literal.

Expected after filling all 15 new indices (no approved seeds in-range):
  - EN translated: 365 (350 + 15)
  - EN incomplete: 670 (685 - 15)
"""

import json
import os
import sys

# ── Translations ──────────────────────────────────────────────────────────
TRANSLATIONS = {
    350: "REINSTALAR TEMA DO BANJO",
    351: "REINSTALADO",
    352: "SEU TEMA FOI REINSTALADO!",
    353: "SUA IMAGEM DE JOGADOR FOI REINSTALADA!",
    354: "REINSTALANDO...",
    355: "AGUARDE ENQUANTO O TEMA É REINSTALADO",
    356: "INSTALANDO...",
    357: "AGUARDE ENQUANTO O TEMA É INSTALADO",
    358: "Falha ao carregar",
    359: "Seu dispositivo de armazenamento foi removido.  Selecione um novo.",
    360: "AVANCE ATÉ ELA E PRESSIONE [0x85] PARA SE TELETRANSPORTAR PARA QUALQUER OUTRA PLATAFORMA DE TELETRANSPORTE QUE VOCÊ TENHA ATIVADO NESTE MUNDO!",
    364: "BASTA AVANÇAR ATÉ A PLATAFORMA E PRESSIONAR [0x85] PARA SE TELETRANSPORTAR.",
    366: "PRESSIONE [0x85] PARA VOLTAR À SUA MISSÃO DE REANIMAR O BOTTLES.",
    369: "ENQUANTO ESTIVER AGARRADO, PRESSIONE [0x86] PARA ATACAR, [0x87] PARA SUBIR ATÉ A BORDA OU [0x85] PARA SOLTAR-SE E CAER.",
    372: "PRESSIONE [0x87] PARA APRENDER O MOVIMENTO, OU [0x85] PARA RECUSAR.",
}

EXPECTED_RANGE = set(range(350, 375))
if not set(TRANSLATIONS).issubset(EXPECTED_RANGE):
    raise RuntimeError("TRANSLATIONS contains indices outside 350..374")

# ── Load source ───────────────────────────────────────────────────────────
with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

# Find actual source indices in range 350-374
actual_indices = sorted([s["index"] for s in src_strings if 350 <= s["index"] <= 374])
expected_entries = sorted(actual_indices)

if set(TRANSLATIONS) != set(expected_entries):
    print(f"ERROR: translation keys {sorted(TRANSLATIONS)} do not exactly cover source {expected_entries}")
    sys.exit(1)
print(f"Source indices 350..374: {len(actual_indices)} entries found")

# ── Build batch artifact ──────────────────────────────────────────────────
batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 350 <= idx <= 374 and idx in TRANSLATIONS:
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
            or translation[:len(translation) - len(translation.rstrip())]
            != source_text[:len(source_text) - len(source_text.rstrip())]
            or translation.count("\n") != source_text.count("\n")):
        preflight_structure_errors.append(idx)
    try:
        translation.encode(src_rec["encoding"])
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
print("Preflight passed: source, structure, and per-record encoding")

batch_artifact = {
    "batch_id": "batch-0350-0374",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": sorted(list(range(350, 375))),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0350-0374.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")

# ── Merge into translated.json ────────────────────────────────────────────
with open("translation/pt-BR/translated.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

trans_map = {idx: TRANSLATIONS[idx] for idx in TRANSLATIONS}
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
if merged_count != len(TRANSLATIONS):
    raise RuntimeError(f"Expected to merge {len(TRANSLATIONS)} records, merged {merged_count}")
print(f"Merged {merged_count} translations into {merged_path}")

# ── Verification ──────────────────────────────────────────────────────────
with open(merged_path, "r", encoding="utf-8") as f:
    verify_data = json.load(f)
vs = verify_data["strings"]

translated_in_range = [s for s in vs if 350 <= s["index"] <= 374 and s.get("translation") is not None]
incomplete_in_range = [s for s in vs if 350 <= s["index"] <= 374 and s.get("translation") is None]
all_translated = [s for s in vs if s.get("translation") is not None]
all_incomplete = [s for s in vs if s.get("translation") is None]
en_strings = [s for s in vs if s["index"] < 1521]
non_en = [s for s in vs if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"")
print(f"Verification:")
print(f"  Translated in range 350..374: {len(translated_in_range)}")
print(f"  Incomplete in range 350..374: {len(incomplete_in_range)}")
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
                    or entry["translation"][:len(entry["translation"]) - len(entry["translation"].rstrip())]
                    != src_rec["text"][:len(src_rec["text"]) - len(src_rec["text"].rstrip())]
                    or entry["translation"].count("\n") != src_rec["text"].count("\n")):
        structure_errors.append(idx)
print(f"Source text mismatches: {len(mismatch)}")
print(f"Leading-space/newline mismatches: {len(structure_errors)}")
if mismatch or structure_errors or null_trans or blank_trans:
    raise RuntimeError("batch source/translation invariants failed")

cp1252_errors = []
for entry in batch_entries:
    try:
        entry["translation"].encode(next(s["encoding"] for s in src_strings if s["index"] == entry["index"]))
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
    print(f"All translations match their source encodings")

print(f"")
print(f"Expected post-merge counts:")
print(f"  Total: {len(vs)} (expected 5174) {'OK' if len(vs) == 5174 else 'MISMATCH'}")
print(f"  Translated: {len(all_translated)} (expected 365) {'OK' if len(all_translated) == 365 else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected 670) {'OK' if len(en_incomplete) == 670 else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected 1035) {'OK' if len(en_strings) == 1035 else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected 4139) {'OK' if len(non_en) == 4139 else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")
if (len(vs), len(all_translated), len(en_incomplete), len(en_strings),
        len(non_en), len(non_en_translated)) != (5174, 365, 670, 1035, 4139, 0):
    raise RuntimeError("post-merge count invariants failed")

# ── Selective TM upsert ───────────────────────────────────────────────────
# Only concise, canonical location/item labels are reusable TM candidates.
# One-off objective sentences and UI strings stay in the batch/glossary.
SELECTIVE_TM_NOTES = {
    358: 'erro UI — Loading failed (padrão "FALHA AO ...")',
    359: 'mensagem de storage device removido (paralelo a 138)',
    360: 'instrução de warp — "WARP PAD" = "PLATAFORMA DE TELETRANSPORTE"',
    364: 'instrução de warp curta — "WARP" = "TELETRANSPORTAR"',
    366: 'instrução de missão — "MOLE-RESTORING QUEST" = "MISSÃO DE REANIMAR O BOTTLES"',
    369: 'mecânica de combate — GRABBING/CLIMB/RELEASE (termos de jogo)',
    372: 'instrução de movimento — LEARN THE MOVE / BE DISMISSED',
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
            "notes": f"batch 0350-0374 - {SELECTIVE_TM_NOTES[idx]}",
        })

tm_path = "translation/pt-BR/tm.json"
with open(tm_path, "r", encoding="utf-8") as f:
    tm_data = json.load(f)

# Remove only this batch's proposed entries that are no longer selected; approved
# entries are immutable. This makes the policy and reruns deterministic.
tm_data["entries"] = [
    e for e in tm_data["entries"]
    if not (350 <= e.get("source_index", -1) <= 374
            and e.get("status") == "proposed"
            and e.get("notes", "").startswith("batch 0350-0374 -"))
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
