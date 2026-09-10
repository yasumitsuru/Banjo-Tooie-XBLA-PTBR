#!/usr/bin/env python3
"""Translate source indices 300..324 to pt-BR and produce batch artifact + merge.

Deterministic: running twice produces byte-identical output.

Terminology decisions for this batch:
  - CHILLY WILLY (308), CHILLI BILLI (308): nomes próprios de chefes —
    manter em inglês.
  - SABREMAN (310): nome próprio de personagem — manter em inglês.
  - BOGGY (311): nome próprio (SRA. BOGGY) — manter; "URSOPOLAR" →
    "URSO POLAR" (termo descritivo).
  - MINGY JONGO (318): nome próprio de chefe — manter em inglês.
  - CANARY MARY (321): nome próprio — manter em inglês.
  - ZUBBA (322): nome próprio de criatura (ZUBBA) — manter em inglês.
  - COLOSSEUM KICKBALL (315): nome de mini-jogo — manter em inglês
    (glossário: "Colosseum Kickball").
  - POT O' GOLD (320): nome de mini-jogo — manter em inglês (glossário).
  - ZUBBA'S HIVE (322): nome de mini-jogo — manter em inglês (glossário).
  - WASTE DISPOSAL PLANT (307): já no TM (298) — "ESTAÇÃO DE TRATAMENTO
    DE RESÍDUOS".
  - CHEESE WEDGE (324): localização descritiva — "CUNHA DE QUEIJO".
  - FLOOR: "ANDAR" — termo comum de localização.
  - TRASH COMPACTOR (305): "COMPACTADOR DE LIXO" — TRASH é termo
    comum (lixo), não nome próprio (FR: "COMPACTEUR D'ORDURES").
  - PACKING GAME (306): "JOGO DA EMBALAGEM" — "packing" é termo
    descritivo (FR: "JEU D'EMPAQUETAGE").
  - COLosseum ARCHES (317): "ARCADAS DO COLOSSEU" — COLOSSEU é nome de
    fase/local mantido.
  - VOLCANO (309): "VULCÃO" — termo comum.
  - OIL DRILL (313): "PERFURADORA DE PETRÓLEO" — termo descritivo
    (ES: "PERFORADORA").
  - ICE TRAIN STATION LINK (312): "CONEXÃO DA ESTAÇÃO DO TREM DE GELO"
    — LINK = conexão (consistente com 314).
  - TERRYDACTYLAND (314): nome próprio de fase — manter em inglês
    (glossário).
  - STOMPING PLAINS (314): topônimo — manter em inglês (glossário).
  - EYEBALL PLANTS (323): "PLANTAS DE OLHO" — "eyeball" é termo
    descritivo (FR: "PLANTES OCULAIRES", ES: "PLANTAS-OJO", IT: "PIANTE OCULOBULBO").
  - UFO ALIENS (316): "ALIENÍGENAS" — "aliens" são os alienígenas,
    não os OVNIs (FR: "ALIENS DE L'OVNI").
  - WIN THE: "VENCER O" — padrão do lote anterior.
  - DEFEAT: "DERROTAR" — padrão do lote anterior.
  - INSIDE THE: "DENTRO DO(A)" — padrão do lote anterior.
  - TOP OF: "NO TOPO DA(O)" — padrão do lote anterior.
  - HELP: "AJUDAR" — infinitivo padrão.
  - COMPLETE: "COMPLETAR" — infinitivo.
  - ACTIVATE: "ATIVAR" — infinitivo.
  - FEED: "ALIMENTAR" — infinitivo.
  - WASH: "LAVAR" — infinitivo.
  - EXTERMINATE: "EXTERMINAR" — infinitivo.

Expected after filling all 25 new indices (no approved seeds in-range):
  - EN translated: 325 (300 + 25)
  - EN incomplete: 710 (735 - 25)
"""

import json
import os
import sys

# ── Translations ──────────────────────────────────────────────────────────
TRANSLATIONS = {
    300: " EXTERMINAR OS CLINKERS NO ANDAR 4",
    301: " LAVAR OS TRABALHADORES SUJOS",
    302: " NO TOPO DAS CAIXAS NO ANDAR 5",
    303: " SALA DE CONTROLE DE QUALIDADE NO ANDAR 4",
    304: " NO TOPO DA PLATAFORMA CENTRAL NO ANDAR 1",
    305: " DENTRO DO COMPACTADOR DE LIXO NO ANDAR 1",
    306: " JOGO DA EMBALAGEM NO ANDAR 3",
    307: " DENTRO DA ESTAÇÃO DE TRATAMENTO DE RESÍDUOS",
    308: " DERROTAR CHILLY WILLY E CHILLI BILLI",
    309: " DENTRO DO VULCÃO",
    310: " AJUDAR O SABREMAN A VOLTAR À SUA BARRACA",
    311: " ALIMENTAR O BOGGY, O URSO POLAR",
    312: " CONEXÃO DA ESTAÇÃO DO TREM DE GELO",
    313: " ATIVAR A PERFURADORA DE PETRÓLEO",
    314: " CONEXÃO COM AS STOMPING PLAINS DE TERRYDACTYLAND",
    315: " VENCER OS JOGOS DE COLOSSEUM KICKBALL",
    316: " AJUDAR OS ALIENÍGENAS",
    317: " DENTRO DAS ARCADAS DO COLOSSEU",
    318: " DERROTAR MINGY JONGO",
    319: " VENCER AS OLIMPÍADAS DO CUCKOO",
    320: " COMPLETAR O JOGO DE POT O' GOLD",
    321: " CORRIDA DO RATO MECÂNICO DA CANARY MARY",
    322: " JOGO DA COLMEIA DO ZUBBA",
    323: " DERROTAR AS PLANTAS DE OLHO",
    324: " DENTRO DA CUNHA DE QUEIJO",
}

EXPECTED_RANGE = set(range(300, 325))
if set(TRANSLATIONS) != EXPECTED_RANGE:
    raise RuntimeError("TRANSLATIONS must contain exactly indices 300..324")

# ── Load source ───────────────────────────────────────────────────────────
with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

expected_indices = list(range(300, 325))
actual_indices = sorted([s["index"] for s in src_strings if 300 <= s["index"] <= 324])
if actual_indices != expected_indices:
    print(f"ERROR: Expected indices {expected_indices}, got {actual_indices}")
    sys.exit(1)
print(f"Source indices 300..324: {len(actual_indices)} entries found")

# ── Build batch artifact ──────────────────────────────────────────────────
batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 300 <= idx <= 324:
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
    "batch_id": "batch-0300-0324",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": list(range(300, 325)),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0300-0324.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")

# ── Merge into translated.json ────────────────────────────────────────────
with open("translation/pt-BR/translated.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

trans_map = {idx: TRANSLATIONS[idx] for idx in range(300, 325)}
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

translated_in_range = [s for s in vs if 300 <= s["index"] <= 324 and s.get("translation") is not None]
incomplete_in_range = [s for s in vs if 300 <= s["index"] <= 324 and s.get("translation") is None]
all_translated = [s for s in vs if s.get("translation") is not None]
all_incomplete = [s for s in vs if s.get("translation") is None]
en_strings = [s for s in vs if s["index"] < 1521]
non_en = [s for s in vs if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"")
print(f"Verification:")
print(f"  Translated in range 300..324: {len(translated_in_range)}")
print(f"  Incomplete in range 300..324: {len(incomplete_in_range)}")
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
print(f"  Translated: {len(all_translated)} (expected 325) {'OK' if len(all_translated) == 325 else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected 710) {'OK' if len(en_incomplete) == 710 else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected 1035) {'OK' if len(en_strings) == 1035 else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected 4139) {'OK' if len(non_en) == 4139 else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")
if (len(vs), len(all_translated), len(en_incomplete), len(en_strings),
        len(non_en), len(non_en_translated)) != (5174, 325, 710, 1035, 4139, 0):
    raise RuntimeError("post-merge count invariants failed")

# ── Selective TM upsert ───────────────────────────────────────────────────
# Only concise, canonical location/item labels are reusable TM candidates.
# One-off objective sentences and mini-game goals stay in the batch/glossary.
SELECTIVE_TM_NOTES = {
    305: 'localização — TRASH COMPACTOR (compactador de lixo)',
    306: 'localização/jogo — PACKING GAME (jogo da embalagem)',
    307: 'localização — WASTE DISPOSAL PLANT (já no TM 298)',
    309: 'localização — VOLCANO',
    312: 'localização — ICE TRAIN STATION LINK (conexão da estação do trem de gelo)',
    313: 'mecânica — OIL DRILL (perfuradora de petróleo)',
    314: 'localização — TERRYDACTYLAND nome próprio, STOMPING PLAINS topônimo',
    317: 'localização — COLOSSEUM ARCHES',
    324: 'localização — CHEESE WEDGE',
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
            "notes": f"batch 0300-0324 - {SELECTIVE_TM_NOTES[idx]}",
        })

tm_path = "translation/pt-BR/tm.json"
with open(tm_path, "r", encoding="utf-8") as f:
    tm_data = json.load(f)

# Remove only this batch's proposed entries that are no longer selected; approved
# entries are immutable. This makes the policy and reruns deterministic.
tm_data["entries"] = [
    e for e in tm_data["entries"]
    if not (300 <= e.get("source_index", -1) <= 324
            and e.get("status") == "proposed"
            and e.get("notes", "").startswith("batch 0300-0324 -"))
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
