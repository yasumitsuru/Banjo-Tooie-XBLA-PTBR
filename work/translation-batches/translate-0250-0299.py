#!/usr/bin/env python3
"""Translate source indices 250..299 to pt-BR and produce batch artifact + merge.

Deterministic: running twice produces byte-identical output.

Terminology decisions for this batch:
  - TARGITZAN (252, 256): nome próprio de chefe — manter em inglês.
  - JADE SNAKE (253, 257): termo descritivo — "SERPENTE DE JADE";
    SSSLUMBER (source 1332) é o nome próprio da criatura.
  - OLD KING COAL (258): nome próprio de chefe — manter em inglês.
  - CANARY MARY (259): nome próprio — manter em inglês.
  - MAYAHEM (263): nome próprio (fase) — manter em inglês.
  - JIGGY (264): nome próprio do coletável — manter em inglês.
  - HOOP HURRY (268), DODGEM DOME (269), SAUCER OF PERIL (271),
    BALLOON BURST (272), DIVE OF DEATH (273): mini-jogos — manter em inglês.
  - MR. PATCH (270), LORD WOO FAK FAK (284), TERRY (288/291/294),
    WELDAR (299): nomes próprios de chefes — manter em inglês.
  - MRS. BOGGY (274), MERRY MAGGIE (283), PAWNO (286): nomes próprios.
  - TIPTUP (279): nome próprio (criatura) — manter em inglês.
  - STYRACOSAURUS (290): tipo de dinossauro — "ESTIRACOSSAUROS".
  - OOGLE BOOGLES (292), CHOMPASAUR (293), ROCKNUTS (296), T-REX (297):
    tipos/nomes de criatura — manter em inglês.
  - STAR SPINNER (275), INFERNO (276): nomes de fase/local — manter.
  - JOLLY (282): nome próprio — manter.
  - SMUGGLER (282): termo descritivo — "contrabandista".
  - WIN THE (250, 268, 269, 272): "VENCER O(S)" — infinitivo padrão.
  - DEFEAT (258, 270, 284, 291, 296, 299): "DERROTAR" — infinitivo.
  - TOP OF (256, 273, 275, 276): "NO TOPO DA(O)" — localização.
  - INSIDE THE (260-262, 280, 282, 285, 286, 293, 298): "DENTRO DO(A)".
  - HATCH (279, 294): "CHOCAR" — consistente com glossário (47).
  - RETURN (294): "DEVOLVER" — consistente com glossário.
  - KICKBALL (250): nome de jogo — manter em inglês.
  - KIDS (274): "CRIANÇAS" — multilingue confirma (FR: enfants, DE: Kinder,
    ES: chicos, IT: bimbi) = filhos/bebês da Sra. Boggy.
  - HANDCART RACE (259): "VAGONETAS" — corrida em vagonetas sobre trilhos.
  - CRUSH (264): "ESMAGAR" — não "ESFAIXAR" (falso cognato).
  - STAR SPINNER (275): nome próprio de atração — manter, não "GIRASSOL".
  - POWER UP THE UFO (287): "RECARREGAR O OVNI" — carregar para deixá-lo pronto.
  - WASTE DISPOSAL PLANT (298): "ESTAÇÃO DE TRATAMENTO DE RESÍDUOS".
  - TRIBE (296): substantivo comum — traduzir como "TRIBO"; ROCKNUTS é o
    nome das criaturas.

Expected after filling all 50 new indices (no approved seeds in-range):
  - EN translated: 300 (250 + 50)
  - EN incomplete: 735 (785 - 50)
"""

import json
import os
import sys

# ── Translations ──────────────────────────────────────────────────────────
TRANSLATIONS = {
    250: " VENCER OS JOGOS DE KICKBALL",
    251: " ELIMINAR A PRAGA DE MOSCAS",
    252: " RECUPERAR O OURO ROUBADO DE TARGITZAN",
    253: " ÁREA DE AREIA MOVEDIÇA NO BOSQUE DA SERPENTE DE JADE",
    254: " ÁREA DE AREIA MOVEDIÇA NO COMPLEXO DA PRISÃO",
    255: " COLUNAS DE PEDRA NO COMPLEXO DA PRISÃO",
    256: " NO TOPO DO TEMPLO DE TARGITZAN",
    257: " SERPENTE DE JADE ADORMECIDA",
    258: " DERROTAR OLD KING COAL",
    259: " CORRIDA DE VAGONETAS DA CANARY MARY",
    260: " DENTRO DA CAVERNA DO GERADOR",
    261: " DENTRO DA CAVERNA DA CASCATA",
    262: " DENTRO DO DEPÓSITO DE MUNIÇÕES",
    263: " RESGATAR O RATO DA PRISÃO DE MAYAHEM",
    264: " ESMAGAR A PEDRA JIGGY E RECOLHER OS PEDAÇOS",
    265: " ATRÁS DA CASCATA EXTERIOR",
    266: " NO PORÃO DA CABANA DE ENERGIA",
    267: " NAS CAVERNAS INUNDADAS",
    268: " VENCER O JOGO DE HOOP HURRY",
    269: " VENCER OS JOGOS DE DODGEM DOME",
    270: " DERROTAR MR. PATCH",
    271: " PASSEIO NO SAUCER OF PERIL",
    272: " VENCER O JOGO DE BALLOON BURST",
    273: " NO TOPO DA PLATAFORMA DO DIVE OF DEATH",
    274: " DEVOLVER AS CRIANÇAS À SRA. BOGGY",
    275: " NO TOPO DO STAR SPINNER",
    276: " NO TOPO DA TORRE DO INFERNO",
    277: " CACTO DA FORÇA",
    278: " JOGO DAS MINAS NA CAVERNA DO FUNDO DO MAR",
    279: " CHOCAR E AJUDAR O BEBÊ TIPTUP",
    280: " DENTRO DO TEMPLO DOS PEIXES",
    281: " LIMPAR E AQUECER A PISCINA",
    282: " DENTRO DA CAVERNA DO CONTRABANDISTA ABAIXO DA TAVERNA DO JOLLY",
    283: " RESGATAR MERRY MAGGIE DE DENTRO DO GRANDE PEIXE",
    284: " DERROTAR LORD WOO FAK FAK",
    285: " DENTRO DE UM PEIXE TRANSPARENTE",
    286: " DENTRO DO EMPÓRIO DO PAWNO",
    287: " RECARREGAR O OVNI",
    288: " SOB O CENTRO DO NINHO DE TERRY",
    289: " ENCHER A PISCINA DO DINOSSAURO SEDENTO",
    290: " AJUDAR A FAMÍLIA DE ESTIRACOSSAUROS",
    291: " DERROTAR TERRY",
    292: " AQUECER OS OOGLE BOOGLES E CONSEGUIR COMIDA PARA ELES",
    293: " DENTRO DA BARRIGA DO CHOMPASAUR",
    294: " CHOCAR E DEVOLVER OS OVOS DE TERRY",
    295: " NAS STOMPING PLAINS",
    296: " DERROTAR A TRIBO DOS ROCKNUTS",
    297: " CÓDIGO DO RUGIDO DO PEQUENO T-REX",
    298: " DENTRO DA ESTAÇÃO DE TRATAMENTO DE RESÍDUOS",
    299: " DERROTAR WELDAR",
}

EXPECTED_RANGE = set(range(250, 300))
if set(TRANSLATIONS) != EXPECTED_RANGE:
    raise RuntimeError("TRANSLATIONS must contain exactly indices 250..299")

# ── Load source ───────────────────────────────────────────────────────────
with open("translation/pt-BR/source.json", "r", encoding="utf-8") as f:
    source_data = json.load(f)

src_strings = source_data["strings"]

expected_indices = list(range(250, 300))
actual_indices = sorted([s["index"] for s in src_strings if 250 <= s["index"] <= 299])
if actual_indices != expected_indices:
    print(f"ERROR: Expected indices {expected_indices}, got {actual_indices}")
    sys.exit(1)
print(f"Source indices 250..299: {len(actual_indices)} entries found")

# ── Build batch artifact ──────────────────────────────────────────────────
batch_entries = []
for s in src_strings:
    idx = s["index"]
    if 250 <= idx <= 299:
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
    "batch_id": "batch-0250-0299",
    "language_pair": "en-US -> pt-BR",
    "assigned_indices": list(range(250, 300)),
    "total_entries": len(batch_entries),
    "entries": batch_entries,
}

batch_path = "work/translation-batches/batch-0250-0299.json"
with open(batch_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(batch_artifact, f, ensure_ascii=False, indent=1, sort_keys=False)
    f.write("\n")
print(f"Batch artifact written to {batch_path}")
print(f"Total entries: {len(batch_entries)}")

# ── Merge into translated.json ────────────────────────────────────────────
with open("translation/pt-BR/translated.json", "r", encoding="utf-8") as f:
    trans_data = json.load(f)

trans_map = {idx: TRANSLATIONS[idx] for idx in range(250, 300)}
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
    raise RuntimeError(f"Expected to merge 50 records, merged {merged_count}")
print(f"Merged {merged_count} translations into {merged_path}")

# ── Verification ──────────────────────────────────────────────────────────
with open(merged_path, "r", encoding="utf-8") as f:
    verify_data = json.load(f)
vs = verify_data["strings"]

translated_in_range = [s for s in vs if 250 <= s["index"] <= 299 and s.get("translation") is not None]
incomplete_in_range = [s for s in vs if 250 <= s["index"] <= 299 and s.get("translation") is None]
all_translated = [s for s in vs if s.get("translation") is not None]
all_incomplete = [s for s in vs if s.get("translation") is None]
en_strings = [s for s in vs if s["index"] < 1521]
non_en = [s for s in vs if s["index"] >= 1521]
en_incomplete = [s for s in en_strings if s.get("translation") is None]
non_en_translated = [s for s in non_en if s.get("translation") is not None]

print(f"")
print(f"Verification:")
print(f"  Translated in range 250..299: {len(translated_in_range)}")
print(f"  Incomplete in range 250..299: {len(incomplete_in_range)}")
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
print(f"  Translated: {len(all_translated)} (expected 300) {'OK' if len(all_translated) == 300 else 'MISMATCH'}")
print(f"  EN incomplete: {len(en_incomplete)} (expected 735) {'OK' if len(en_incomplete) == 735 else 'MISMATCH'}")
print(f"  EN: {len(en_strings)} (expected 1035) {'OK' if len(en_strings) == 1035 else 'MISMATCH'}")
print(f"  Non-EN: {len(non_en)} (expected 4139) {'OK' if len(non_en) == 4139 else 'MISMATCH'}")
print(f"  Non-EN translated: {len(non_en_translated)}")
if (len(vs), len(all_translated), len(en_incomplete), len(en_strings),
        len(non_en), len(non_en_translated)) != (5174, 300, 735, 1035, 4139, 0):
    raise RuntimeError("post-merge count invariants failed")

# ── Selective TM upsert ───────────────────────────────────────────────────
# Only concise, canonical location/item labels are reusable TM candidates.
# One-off objective sentences and mini-game goals stay in the batch/glossary.
SELECTIVE_TM_NOTES = {
    253: 'localização — SERPENTE DE JADE, termo descritivo',
    254: 'localização — PRISON COMPOUND',
    255: 'localização — PRISON COMPOUND',
    256: 'localização — TARGITZAN nome próprio',
    257: 'criatura — SERPENTE DE JADE, termo descritivo',
    260: 'localização — GENERATOR CAVERN',
    261: 'localização — WATERFALL CAVERN',
    262: 'localização — ORDNANCE STORAGE',
    265: 'localização — EXTERIOR WATERFALL',
    266: 'localização — POWER HUT',
    267: 'localização — FLOODED CAVES',
    273: 'localização — DIVE OF DEATH mini-jogo',
    275: 'localização — STAR SPINNER',
    276: 'localização — INFERNO',
    277: 'item — CACTO DA FORÇA',
    278: 'localização/jogo — SEA BOTTOM',
    280: 'localização — TEMPLE OF THE FISHES',
    282: 'localização — SMUGGLER/contrabandista, taverna do JOLLY',
    285: 'localização — PEIXE TRANSPARENTE',
    286: 'localização — PAWNO nome próprio',
    288: 'localização — TERRY nome próprio',
    293: 'localização — CHOMPASAUR criatura',
    295: 'localização — STOMPING PLAINS',
    298: 'localização — WASTE DISPOSAL PLANT',
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
            "notes": f"batch 0250-0299 - {SELECTIVE_TM_NOTES[idx]}",
        })

tm_path = "translation/pt-BR/tm.json"
with open(tm_path, "r", encoding="utf-8") as f:
    tm_data = json.load(f)

# Remove only this batch's proposed entries that are no longer selected; approved
# entries are immutable. This makes the policy and reruns deterministic.
tm_data["entries"] = [
    e for e in tm_data["entries"]
    if not (250 <= e.get("source_index", -1) <= 299
            and e.get("status") == "proposed"
            and e.get("notes", "").startswith("batch 0250-0299 -"))
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
