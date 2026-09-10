#!/usr/bin/env python3
"""Translate source indices 400..424 to pt-BR and produce batch artifact + merge.

Deterministic: running twice produces byte-identical output.

Source indices in range 400-424 (15 entries, gaps at 401/403/405/407/409/411/417/418/421/424):
  400: SELECT A DESTINATION. [0x87] SELECT [0x85] CANCEL
  402: SELECT FLOOR, PLEASE? [0x87] SELECT [0x85] CANCEL
  404: WHERE Y' GOING, PUNK? [0x87] SELECT [0x85] CANCEL
  406: PICK A WORLD TO PLAY. [0x87] SELECT [0x85] CANCEL
  408: PICK A TRACK TO PLAY. [0x87] SELECT [0x85] CANCEL
  410: CHOOSE A DESTINATION. [0x87] SELECT [0x85] CANCEL
  412: [0x87] YES [0x85] NO
  413: [0x87] AYE [0x85] NAW
  414: [0x87] YUS [0x85] NOPE
  415: [0x85] NO
  416: PRESS [0x88] OR [0x81] TO FIRE EGGS AND USE [0x89] OR [0x80] TO TOGGLE THE AIMING SIGHT ON AND OFF.
  419: TAP [0x89] OR [0x80] TO GET YOUR EGGS ON VIEW,
  420: YOU CAN ALSO BRING THE CAMERA LEVEL BY PRESSING [0x89] OR [0x80].
  422: SELECT THESE EGGS BY PRESSING [0x89] OR [0x80] UNTIL THEY ARE HIGHLIGHTED.
  423: WHEN IN BREEGULL BLASTER SECTIONS, ACTIVATE THE AIMING SIGHT BY HOLDING [0x89] OR [0x80].

Terminology decisions for this batch:
  - SELECT (400/402/404/406/408/410/422): "SELECIONE" - verb imperative,
    UI padrao (glossario indice 102 = SELECIONAR, mas como verbo
    imperativo em frases UI pt-BR usa "SELECIONE").
  - DESTINATION (400/410): "DESTINO" - termo padrao.
  - FLOOR (402): "ANDAR" - andar de predio/edificio (contexto elevador).
  - WHERE Y' GOING, PUNK (404): "PARA ONDE VAI, MOLEQUE?" - "PUNK" como
    tratamento confrontacional/comico; "MOLEQUE" e o equivalente pt-BR
    natural para o tom de "PUNK" (paralelo ES "GAMBERRO", DE "DU NULL").
  - PICK A WORLD/TRACK (406/408): "ESCOLHA UM MUNDO/FAIXA" - paralelo a
    CHOOSE A DESTINATION (410); glossario padroniza PICK/CHOOSE -> ESCOLHA.
    TRACK (408) = faixa musical (Jiggys Jamboree), confirmado por DE "SONG",
    ES "TEMA", IT "MELODIA"; "FAIXA" e o termo pt-BR padrao para faixa musical;
    "PARA REPRODUZIR" evita confundir faixa musical com jogar uma partida.
  - CHOOSE A DESTINATION (410): "ESCOLHA UM DESTINO" - paralelo a 406.
  - YES/NO (412): "SIM / NAO" - UI padrao (paralelo a 397 "TEM CERTEZA?
    [0x87] SIM, [0x85] NAO.").
  - AYE/NAW (413): "TÁ / NÃO TÁ" - sim/nao comico/dialetal localizado em pt-BR
    (todas as outras linguas localizam: FR OUAIP/NAN, DE AI AI/NE, ES
    SIGH/NOGH, IT OK/MHM); UI em pt-BR conforme politica do README.
  - YUS/NOPE (414): "TÁ / NÃO" - sim/nao comico localizado em pt-BR
    (paralelo a 413; FR OUICHE/NAN, DE JAWOLLJA/N', ES SIP/NOP, IT SSSl/NOOO).
  - NO (415): "NAO" - UI padrao.
  - FIRE EGGS (416): "DISPARAR OVOS" - consistente com glossario
    "Egg Firing" = "Disparo de Ovos" (indice 38).
  - AIMING SIGHT (416/423): "mira" - termo de jogo;
    "AIMING SIGHT" = "MIRA" (glossario indice 43 = "Mira de Ovos").
  - TAP (419): "PRESSIONE" - padrao UI pt-BR (paralelo a "PRESS" =
    "PRESSIONE" em todo o glossario). "GET YOUR EGGS ON VIEW" = "EXIBIR
    SEUS OVOS", indicando a exibição dos tipos de ovos para o ciclo descrito
    pelos índices 419/422; a vírgula final é preservada.
  - BRING THE CAMERA LEVEL (420): "NIVELAR A CAMARA" - termo de camera
    em jogos; "level" como verbo = nivelar.
  - HIGHLIGHTED (422): "DESTACADO" - termo padrao de UI.
  - BREEGULL BLASTER (423): "Lançador Breegull" - glossario indice 43;
    "NAS SEÇÕES DO LANÇADOR BREEGULL" fornece os artigos naturais.

Expected after filling all 15 new indices:
  - EN translated: 392 (377 + 15)
  - EN incomplete: 643 (658 - 15)
"""

import json
import os
import sys

# -- Translations --
TRANSLATIONS = {
    400: "SELECIONE UM DESTINO.\n[0x87] SELECIONAR [0x85] CANCELAR",
    402: "SELECIONE O ANDAR, POR FAVOR?\n[0x87] SELECIONAR [0x85] CANCELAR",
    404: "PARA ONDE VAI, MOLEQUE?\n[0x87] SELECIONAR [0x85] CANCELAR",
    406: "ESCOLHA UM MUNDO PARA JOGAR.\n[0x87] SELECIONAR [0x85] CANCELAR",
    408: "ESCOLHA UMA FAIXA PARA REPRODUZIR.\n[0x87] SELECIONAR [0x85] CANCELAR",
    410: "ESCOLHA UM DESTINO.\n[0x87] SELECIONAR [0x85] CANCELAR",
    412: "[0x87] SIM [0x85] NÃO",
    413: "[0x87] TÁ [0x85] NÃO TÁ",
    414: "[0x87] TÁ [0x85] NÃO",
    415: "[0x85] NÃO",
    416: "PRESSIONE [0x88] OU [0x81] PARA DISPARAR OVOS E USE [0x89] OU [0x80] PARA LIGAR E DESLIGAR A MIRA.",
    419: "PRESSIONE [0x89] OU [0x80] PARA EXIBIR SEUS OVOS,",
    420: "VOCÊ TAMBÉM PODE NIVELAR A CÂMERA PRESSIONANDO [0x89] OU [0x80].",
    422: "SELECIONE ESTES OVOS PRESSIONANDO [0x89] OU [0x80] ATÉ QUE ELES SEJAM DESTACADOS.",
    423: "NAS SEÇÕES DO LANÇADOR BREEGULL, ATIVE A MIRA SEGURANDO [0x89] OU [0x80]."
}

EXPECTED_RANGE = set(range(400, 425))
if not set(TRANSLATIONS).issubset(EXPECTED_RANGE):
    raise RuntimeError("TRANSLATIONS contains indices outside 400..424")

# -- Load source --
with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

# Find actual source indices in range 400-424
actual_indices = sorted([s["index"] for s in src_strings if 400 <= s["index"] <= 424])
expected_entries = sorted(actual_indices)

if set(TRANSLATIONS) != set(expected_entries):
    print(f"ERROR: translation keys {sorted(TRANSLATIONS)} do not exactly cover source {expected_entries}")
    sys.exit(1)
print(f"Source indices 400..424: {len(actual_indices)} entries found: {actual_indices}")

# -- Build batch artifact --
batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 400 <= idx <= 424 and idx in TRANSLATIONS:
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
    "batch_id": "batch-0400-0424",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": sorted(list(range(400, 425))),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0400-0424.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")

# -- Merge into translated.json --
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

# -- Verification --
with open(merged_path, "r", encoding="utf-8") as f:
    verify_data = json.load(f)
vs = verify_data["strings"]

translated_in_range = [s for s in vs if 400 <= s["index"] <= 424 and s.get("translation") is not None]
incomplete_in_range = [s for s in vs if 400 <= s["index"] <= 424 and s.get("translation") is None]
all_translated = [s for s in vs if s.get("translation") is not None]
all_incomplete = [s for s in vs if s.get("translation") is None]
en_strings = [s for s in vs if s["index"] < 1521]
non_en = [s for s in vs if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"")
print(f"Verification:")
print(f"  Translated in range 400..424: {len(translated_in_range)}")
print(f"  Incomplete in range 400..424: {len(incomplete_in_range)}")
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
print(f"  Translated: {len(all_translated)} (expected 392) {'OK' if len(all_translated) == 392 else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected 643) {'OK' if len(en_incomplete) == 643 else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected 1035) {'OK' if len(en_strings) == 1035 else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected 4139) {'OK' if len(non_en) == 4139 else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")
if (len(vs), len(all_translated), len(en_incomplete), len(en_strings),
        len(non_en), len(non_en_translated)) != (5174, 392, 643, 1035, 4139, 0):
    raise RuntimeError("post-merge count invariants failed")

# -- Selective TM upsert --
# Only reusable terminology decisions enter the TM. One-off objective
# sentences and UI strings stay in the batch artifact.
SELECTIVE_TM_NOTES = {
    416: 'EGG AIMING - "FIRE EGGS" = "DISPARAR OVOS" (glossario); "AIMING SIGHT" = "MIRA" (glossario indice 43)',
    423: 'BREEGULL BLASTER = "LANÇADOR BREEGULL" (glossario indice 43; nome proprio Breegull mantido)',
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
            "notes": f"batch 0400-0424 - {SELECTIVE_TM_NOTES[idx]}",
        })

tm_path = "translation/pt-BR/tm.json"
with open(tm_path, "r", encoding="utf-8") as f:
    tm_data = json.load(f)

# Remove only this batch's proposed entries that are no longer selected; approved
# entries are immutable. This makes the policy and reruns deterministic.
tm_data["entries"] = [
    e for e in tm_data["entries"]
    if not (400 <= e.get("source_index", -1) <= 424
            and e.get("status") == "proposed"
            and e.get("notes", "").startswith("batch 0400-0424 -"))
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
